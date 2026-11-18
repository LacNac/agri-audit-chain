import os
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any
import psycopg2
from fastapi import HTTPException

from .audit_trail_service import record_audit_trail
from .cold_chain_service import enqueue_batch_sync, process_cold_chain_outbox
from .notification_service import create_notification

logger = logging.getLogger(__name__)


def generate_batch_code() -> str:
    return f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def create_batch(db: sqlite3.Connection, payload: dict[str, Any], farmer_id: int | None = None):
    if farmer_id is None:
        raise HTTPException(status_code=401, detail="Không xác định farmer hiện tại")

    clean_payload = dict(payload)
    clean_payload.pop("farmer_id", None)

    product_name = clean_payload.get("product_name")
    product_type = clean_payload.get("product_type")
    origin = clean_payload.get("origin")
    quantity = clean_payload.get("quantity")
    unit = clean_payload.get("unit")
    production_date = clean_payload.get("production_date")
    note = clean_payload.get("note")

    if not product_name or not product_type or not origin or quantity is None or not unit:
        raise HTTPException(status_code=400, detail="Thiếu thông tin bắt buộc của Batch")

    producer_name = clean_payload.get("producer_name")
    try:
        farmer_row = db.execute("SELECT full_name FROM users WHERE id = ?", (farmer_id,)).fetchone()
        if not producer_name and farmer_row:
            producer_name = farmer_row[0]
    except (sqlite3.DatabaseError, psycopg2.Error):
        farmer_row = None

    cursor = db.cursor()
    batch_code = generate_batch_code()

    cursor.execute(
        """
        INSERT INTO batches (
            batch_code, product_name, product_type, producer_name, origin, quantity, unit,
            destination, production_date, expiry_date, status, farmer_id, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'UNVERIFIED', ?, ?)
        """,
        (
            batch_code,
            product_name,
            product_type,
            producer_name,
            origin,
            quantity,
            unit,
            clean_payload.get("destination"),
            production_date,
            clean_payload.get("expiry_date"),
            farmer_id,
            note,
        ),
    )
    batch_id = cursor.lastrowid
    db.commit()
    record_audit_trail(db, user_id=farmer_id, action="CREATE_BATCH", entity_type="batch", entity_id=batch_id, old_value=None, new_value={"batch_code": batch_code, "product_name": product_name, "status": "UNVERIFIED"})
    enqueue_batch_sync(db, batch_id)
    process_cold_chain_outbox(db)
    return {"id": batch_id, "batch_code": batch_code, "status": "UNVERIFIED"}


def list_batches(db: sqlite3.Connection, farmer_id: int | None = None):
    if farmer_id is not None:
        rows = db.execute(
            "SELECT * FROM batches WHERE farmer_id = ? ORDER BY id DESC",
            (farmer_id,),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM batches ORDER BY id DESC").fetchall()

    columns = [col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()]
    return [dict(zip(columns, row)) for row in rows]


def get_batch_by_id(db: sqlite3.Connection, batch_id: int):
    row = db.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    columns = [col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()]
    return dict(zip(columns, row))


def update_batch(db: sqlite3.Connection, batch_id: int, payload: dict[str, Any], farmer_id: int):
    batch = get_batch_by_id(db, batch_id)

    if batch["farmer_id"] != farmer_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa batch này")

    if batch["status"] not in {"UNVERIFIED", "REJECTED"}:
        raise HTTPException(status_code=403, detail="Batch ở trạng thái AUDITED, không được sửa hoặc xóa")

    if batch["status"] == "REJECTED":
        if batch.get("return_goods") or batch.get("return_requested"):
            raise HTTPException(
                status_code=400,
                detail="Lô hàng đã được yêu cầu trả hàng về kho lạnh, không thể cập nhật thông tin",
            )

    if "status" in payload:
        raise HTTPException(status_code=400, detail="Status batch chỉ được thay đổi bởi Auditor approve/reject")

    allowed_fields = {
        "product_name",
        "product_type",
        "origin",
        "destination",
        "quantity",
        "unit",
        "production_date",
        "expiry_date",
        "note",
    }
    updates = {key: value for key, value in payload.items() if key in allowed_fields and value is not None}
    if not updates:
        return batch

    previous = get_batch_by_id(db, batch_id)
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [batch_id]
    db.execute(f"UPDATE batches SET {assignments} WHERE id = ?", values)
    if batch["status"] == "REJECTED":
        existing_cols = {col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()}
        reset_fields = ["status = 'UNVERIFIED'"]
        if "reason" in existing_cols:
            reset_fields.append("reason = NULL")
        if "return_goods" in existing_cols:
            reset_fields.append("return_goods = 0")
        if "rejected_at" in existing_cols:
            reset_fields.append("rejected_at = NULL")
        if "return_requested" in existing_cols:
            reset_fields.append("return_requested = 0")
        db.execute(f"UPDATE batches SET {', '.join(reset_fields)} WHERE id = ?", (batch_id,))

        create_notification(
            db,
            recipient_role="COLD_CHAIN",
            title=f"Nông dân đã cập nhật lại lô hàng {batch['batch_code']}",
            message=f"Nông dân đã chỉnh sửa thông tin cho lô hàng {batch.get('product_name', '')} ({batch['batch_code']}). Lô hàng chuyển lại trạng thái UNVERIFIED để chờ kiểm định.",
            batch_id=batch_id,
            notification_type="BATCH_UPDATED",
        )
        create_notification(
            db,
            recipient_role="AUDITOR",
            title=f"Lô hàng {batch['batch_code']} được gửi lại kiểm định",
            message=f"Lô hàng {batch.get('product_name', '')} ({batch['batch_code']}) đã được cập nhật và sẵn sàng kiểm định lại.",
            batch_id=batch_id,
            notification_type="BATCH_UPDATED",
        )

    db.commit()
    record_audit_trail(db, user_id=farmer_id, action="UPDATE_BATCH", entity_type="batch", entity_id=batch_id, old_value={k: previous.get(k) for k in updates}, new_value={k: updates[k] for k in updates})
    enqueue_batch_sync(db, batch_id)
    process_cold_chain_outbox(db)
    return get_batch_by_id(db, batch_id)


def process_expired_rejected_batches(
    db: sqlite3.Connection,
    timeout_hours: float | None = None,
) -> list[dict[str, Any]]:
    if timeout_hours is None:
        timeout_env = os.getenv("AUTO_RETURN_TIMEOUT_HOURS")
        seconds_env = os.getenv("AUTO_RETURN_TIMEOUT_SECONDS")
        if seconds_env:
            timeout_seconds = float(seconds_env)
        elif timeout_env:
            timeout_seconds = float(timeout_env) * 3600
        else:
            timeout_seconds = 24.0 * 3600
    else:
        timeout_seconds = float(timeout_hours) * 3600

    rows = db.execute(
        """
        SELECT id, batch_code, product_name, producer_name, farmer_id, rejected_at
        FROM batches
        WHERE status = 'REJECTED'
          AND (return_goods = 0 OR return_goods IS FALSE OR return_goods IS NULL)
          AND (return_requested = 0 OR return_requested IS FALSE OR return_requested IS NULL)
          AND rejected_at IS NOT NULL
        """
    ).fetchall()

    now = datetime.now()
    processed = []

    for row in rows:
        batch_id, batch_code, product_name, producer_name, farmer_id, rejected_at_val = row
        if not rejected_at_val:
            continue

        try:
            if isinstance(rejected_at_val, datetime):
                rejected_dt = rejected_at_val
            else:
                s = str(rejected_at_val).strip()
                if "T" in s:
                    rejected_dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                elif " " in s:
                    rejected_dt = datetime.strptime(s.split(".")[0], "%Y-%m-%d %H:%M:%S")
                else:
                    rejected_dt = datetime.strptime(s, "%Y-%m-%d")
        except (TypeError, ValueError) as error:
            logger.warning(
                "Skipping rejected batch %s because rejected_at is invalid: %s",
                batch_id,
                error,
            )
            continue

        if rejected_dt.tzinfo is not None:
            now_dt = datetime.now(timezone.utc)
        else:
            now_dt = now

        elapsed = (now_dt - rejected_dt).total_seconds()
        if elapsed >= timeout_seconds:
            db.execute(
                """
                UPDATE batches
                SET return_goods = 1,
                    return_requested = 1
                WHERE id = ?
                """,
                (batch_id,),
            )

            create_notification(
                db,
                recipient_role="COLD_CHAIN",
                title=f"Quá hạn 24h: Yêu cầu trả hàng cho lô {batch_code}",
                message=f"Lô hàng {product_name or ''} ({batch_code}) của nông dân {producer_name or ''} đã quá 24h không được cập nhật thông tin. Hệ thống tự động gửi thông báo đến công ty kho lạnh yêu cầu trả hàng cho Farmer.",
                batch_id=batch_id,
                notification_type="RETURN_REQUESTED",
            )
            create_notification(
                db,
                recipient_role="FARMER",
                recipient_user_id=farmer_id,
                title=f"Quá hạn 24h: Lô hàng {batch_code} đã được yêu cầu trả lại",
                message=f"Lô hàng {product_name or ''} ({batch_code}) đã quá 24h không được cập nhật lại thông tin. Hệ thống đã gửi yêu cầu đến công ty kho lạnh để trả hàng cho bạn.",
                batch_id=batch_id,
                notification_type="RETURN_REQUESTED",
            )
            record_audit_trail(
                db,
                user_id=None,
                action="AUTO_RETURN_GOODS_EXPIRED",
                entity_type="batch",
                entity_id=batch_id,
                old_value={"return_goods": False, "return_requested": False},
                new_value={"return_goods": True, "return_requested": True, "elapsed_seconds": elapsed},
            )
            enqueue_batch_sync(db, batch_id)
            processed.append({"batch_id": batch_id, "batch_code": batch_code, "elapsed_seconds": elapsed})

    if processed:
        db.commit()
        process_cold_chain_outbox(db)
    return processed


def delete_batch(db: sqlite3.Connection, batch_id: int, farmer_id: int):
    batch = get_batch_by_id(db, batch_id)

    if batch["farmer_id"] != farmer_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa batch này")

    if batch["status"] in {"UNVERIFIED", "REJECTED"}:
        db.execute("DELETE FROM batches WHERE id = ?", (batch_id,))
        db.commit()
        return {"batch_id": batch_id, "deleted": True}

    raise HTTPException(status_code=403, detail="Batch ở trạng thái AUDITED, không được sửa hoặc xóa")


def submit_batch(db: sqlite3.Connection, batch_id: int, farmer_id: int, resubmit: bool = False):
    batch = get_batch_by_id(db, batch_id)
    if batch["farmer_id"] != farmer_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền gửi batch này")
    expected_status = "REJECTED" if resubmit else "UNVERIFIED"
    if batch["status"] != expected_status:
        raise HTTPException(status_code=400, detail=f"Batch phải ở trạng thái {expected_status}")
    record_audit_trail(
        db,
        user_id=farmer_id,
        action="RESUBMIT_BATCH" if resubmit else "SUBMIT_BATCH",
        entity_type="batch",
        entity_id=batch_id,
        old_value={"status": batch["status"]},
        new_value={"status": batch["status"]},
    )
    return {"batch_id": batch_id, "status": batch["status"], "submitted": True}
