import json
import logging
import os
import sqlite3
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from fastapi import HTTPException

logger = logging.getLogger(__name__)
_missing_secret_warned = False
COLD_CHAIN_API_DEFAULT_URL = "https://cold-chain-telemetry-system-1.onrender.com/api"


def get_cold_chain_data(endpoint: str, params: dict | None = None):
    base_url = os.getenv(
        "COLD_CHAIN_API_BASE_URL",
        COLD_CHAIN_API_DEFAULT_URL,
    ).rstrip("/")
    parsed_base_url = urlsplit(base_url)
    if parsed_base_url.scheme not in {"http", "https"} or not parsed_base_url.netloc:
        raise HTTPException(
            status_code=503,
            detail="COLD_CHAIN_API_BASE_URL phải là URL HTTP hoặc HTTPS hợp lệ",
        )

    query = urlencode({key: value for key, value in (params or {}).items() if value is not None})
    url = f"{base_url}/{endpoint.lstrip('/')}"
    if query:
        url = f"{url}?{query}"

    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Cold Chain API trả về HTTP {error.code}",
        ) from error
    except (URLError, TimeoutError, OSError) as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể kết nối Cold Chain API; hãy kiểm tra server và COLD_CHAIN_API_BASE_URL",
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=502,
            detail="Cold Chain API trả về dữ liệu JSON không hợp lệ",
        ) from error


def is_batch_in_transit(batch_code: str) -> bool:
    payload = get_cold_chain_data("vehicles")
    if isinstance(payload, dict) and payload.get("success") is False:
        raise HTTPException(
            status_code=502,
            detail="Cold Chain API không thể cung cấp trạng thái vận chuyển",
        )
    vehicles = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(vehicles, list):
        raise HTTPException(
            status_code=502,
            detail="Cold Chain API trả về danh sách phương tiện không hợp lệ",
        )

    normalized_batch_code = str(batch_code or "").strip().casefold()
    transit_statuses = {
        "INTRANSIT",
        "INPROGRESS",
        "ONGOING",
        "SHIPPING",
        "DELIVERING",
        "ONTHEROAD",
        "PICKEDUP",
    }
    for vehicle in vehicles:
        if not isinstance(vehicle, dict):
            continue
        vehicle_batch_code = str(vehicle.get("active_batch_code") or "").strip().casefold()
        shipment_status = "".join(
            character
            for character in str(vehicle.get("shipment_status") or "").upper()
            if character.isalnum()
        )
        if (
            vehicle_batch_code == normalized_batch_code
            and shipment_status in transit_statuses
        ):
            return True
    return False


def ensure_batch_not_in_transit(batch_code: str) -> None:
    if is_batch_in_transit(batch_code):
        raise HTTPException(
            status_code=409,
            detail="Lô hàng đang vận chuyển và chưa thể kiểm định",
        )


def enqueue_batch_sync(db, batch_id: int) -> None:
    if isinstance(db, sqlite3.Connection):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
            """
        )
    else:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id SERIAL PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP WITHOUT TIME ZONE,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
            """
        )
    columns = [column[1] for column in db.execute("PRAGMA table_info(batches)").fetchall()]
    row = db.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise RuntimeError(f"Cannot synchronize missing batch {batch_id}")

    batch = dict(zip(columns, row))
    payload = {
        "agri_batch_id": batch["id"],
        "batch_code": batch["batch_code"],
        "product_name": batch["product_name"],
        "product_type": batch.get("product_type"),
        "farmer_name": batch.get("producer_name"),
        "origin": batch.get("origin"),
        "destination": batch.get("destination"),
        "quantity": batch.get("quantity"),
        "unit": batch.get("unit"),
        "status": batch.get("status"),
        "reason": batch.get("reason"),
        "return_goods": bool(batch.get("return_goods")),
        "return_requested": bool(batch.get("return_requested")),
    }
    db.execute(
        "INSERT INTO cold_chain_sync_outbox (payload) VALUES (?)",
        (json.dumps(payload, ensure_ascii=False),),
    )
    db.commit()


def process_cold_chain_outbox(db, limit: int = 100) -> int:
    global _missing_secret_warned

    if isinstance(db, sqlite3.Connection):
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
            """
        )
    else:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id SERIAL PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP WITHOUT TIME ZONE,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
            """
        )

    secret = os.getenv("COLD_CHAIN_INTEGRATION_SECRET", "").strip()
    if not secret:
        if not _missing_secret_warned:
            logger.warning(
                "Cold Chain batch synchronization is disabled; set "
                "COLD_CHAIN_INTEGRATION_SECRET in both applications."
            )
            _missing_secret_warned = True
        return 0

    rows = db.execute(
        """
        SELECT id, payload FROM cold_chain_sync_outbox
        WHERE synced_at IS NULL
        ORDER BY id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    synced = 0
    for outbox_id, payload in rows:
        try:
            _post_cold_chain_batch(payload, secret)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            db.execute(
                """
                UPDATE cold_chain_sync_outbox
                SET attempts = attempts + 1, last_error = ?
                WHERE id = ?
                """,
                (str(error)[:1000], outbox_id),
            )
            db.commit()
            logger.warning(
                "Cold Chain sync for outbox event %s failed; it will be retried: %s",
                outbox_id,
                error,
            )
            continue

        db.execute(
            """
            UPDATE cold_chain_sync_outbox
            SET synced_at = CURRENT_TIMESTAMP, attempts = attempts + 1, last_error = NULL
            WHERE id = ?
            """,
            (outbox_id,),
        )
        db.commit()
        synced += 1
    return synced


def _post_cold_chain_batch(payload: str, secret: str) -> None:
    base_url = os.getenv(
        "COLD_CHAIN_API_BASE_URL",
        COLD_CHAIN_API_DEFAULT_URL,
    ).rstrip("/")
    parsed_base_url = urlsplit(base_url)
    if parsed_base_url.scheme not in {"http", "https"} or not parsed_base_url.netloc:
        raise ValueError("COLD_CHAIN_API_BASE_URL phải là URL HTTP hoặc HTTPS hợp lệ")

    request = Request(
        f"{base_url}/integration/batches",
        data=payload.encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Integration-Key": secret,
        },
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        response.read()
