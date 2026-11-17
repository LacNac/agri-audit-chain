import json
import sqlite3
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from app.services import audit_service, cold_chain_service
from app.services.batch_service import create_batch, process_expired_rejected_batches


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return b'{"success":true}'


def _batch_database():
    db = sqlite3.connect(":memory:")
    db.execute(
        """
        CREATE TABLE batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_code TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            product_type TEXT,
            producer_name TEXT,
            origin TEXT,
            destination TEXT,
            quantity REAL,
            unit TEXT,
            production_date DATE,
            expiry_date DATE,
            status TEXT NOT NULL DEFAULT 'UNVERIFIED',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            farmer_id INTEGER,
            note TEXT,
            reason TEXT,
            rejected_at DATETIME,
            return_goods INTEGER DEFAULT 0,
            return_requested INTEGER DEFAULT 0
        )
        """
    )
    return db


def test_batch_creation_queues_and_sends_snapshot_to_cold_chain(monkeypatch):
    observed = {}

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["payload"] = json.loads(request.data)
        observed["secret"] = request.get_header("X-integration-key")
        observed["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("COLD_CHAIN_INTEGRATION_SECRET", "test-shared-key")
    monkeypatch.setenv("COLD_CHAIN_API_BASE_URL", "http://cold-chain.test/api")
    monkeypatch.setattr(cold_chain_service, "urlopen", fake_urlopen)

    db = _batch_database()
    result = create_batch(
        db,
        {
            "product_name": "Rice",
            "product_type": "Cereal",
            "origin": "Nam Dinh",
            "destination": "Hanoi Market",
            "quantity": 120,
            "unit": "kg",
        },
        farmer_id=7,
    )

    assert result["status"] == "UNVERIFIED"
    assert observed == {
        "url": "http://cold-chain.test/api/integration/batches",
        "payload": {
            "agri_batch_id": result["id"],
            "batch_code": result["batch_code"],
            "product_name": "Rice",
            "product_type": "Cereal",
            "farmer_name": None,
            "origin": "Nam Dinh",
            "destination": "Hanoi Market",
            "quantity": 120.0,
            "unit": "kg",
            "status": "UNVERIFIED",
            "reason": None,
            "return_goods": False,
            "return_requested": False,
        },
        "secret": "test-shared-key",
        "timeout": 5,
    }
    outbox = db.execute(
        "SELECT synced_at, attempts, last_error FROM cold_chain_sync_outbox"
    ).fetchone()
    assert outbox[0] is not None
    assert outbox[1:] == (1, None)


def test_failed_cold_chain_sync_is_retained_and_can_be_retried(monkeypatch):
    monkeypatch.setenv("COLD_CHAIN_INTEGRATION_SECRET", "test-shared-key")
    db = _batch_database()
    db.execute(
        """
        INSERT INTO batches (batch_code, product_name, origin, destination, quantity, unit, farmer_id)
        VALUES ('BATCH-1', 'Rice', 'Nam Dinh', 'Hanoi', 50, 'kg', 7)
        """
    )
    cold_chain_service.enqueue_batch_sync(db, 1)
    monkeypatch.setattr(
        cold_chain_service,
        "urlopen",
        lambda request, timeout: (_ for _ in ()).throw(OSError("connection refused")),
    )

    assert cold_chain_service.process_cold_chain_outbox(db) == 0
    failed = db.execute(
        "SELECT synced_at, attempts, last_error FROM cold_chain_sync_outbox"
    ).fetchone()
    assert failed[0] is None
    assert failed[1] == 1
    assert "connection refused" in failed[2]

    monkeypatch.setattr(cold_chain_service, "urlopen", lambda request, timeout: FakeResponse())
    assert cold_chain_service.process_cold_chain_outbox(db) == 1
    retried = db.execute(
        "SELECT synced_at, attempts, last_error FROM cold_chain_sync_outbox"
    ).fetchone()
    assert retried[0] is not None
    assert retried[1:] == (2, None)


def test_rejected_batch_without_return_request_is_returned_after_24_hours(monkeypatch):
    monkeypatch.delenv("COLD_CHAIN_INTEGRATION_SECRET", raising=False)
    db = _batch_database()
    db.execute(
        """
        INSERT INTO batches (
            batch_code, product_name, producer_name, origin, destination, quantity,
            unit, status, farmer_id, reason, rejected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'REJECTED', ?, ?, ?)
        """,
        (
            "BATCH-RETURN",
            "Rice",
            "Farmer A",
            "Nam Dinh",
            "Hanoi",
            50,
            "kg",
            7,
            "Thông tin sản phẩm không chính xác",
            (datetime.now() - timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.execute(
        """
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_user_id INTEGER,
            recipient_role TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            batch_id INTEGER,
            notification_type TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    processed = process_expired_rejected_batches(db, timeout_hours=24)

    assert processed[0]["batch_code"] == "BATCH-RETURN"
    assert db.execute(
        "SELECT return_goods, return_requested FROM batches WHERE id = 1"
    ).fetchone() == (1, 1)
    notices = db.execute(
        "SELECT recipient_role, notification_type FROM notifications ORDER BY id"
    ).fetchall()
    assert notices == [("COLD_CHAIN", "RETURN_REQUESTED"), ("FARMER", "RETURN_REQUESTED")]
    assert db.execute(
        "SELECT payload FROM cold_chain_sync_outbox ORDER BY id DESC LIMIT 1"
    ).fetchone()[0].find('"return_requested": true') >= 0


def test_reject_batch_is_blocked_while_transporting(monkeypatch):
    db = _batch_database()
    db.execute(
        "INSERT INTO batches (batch_code, product_name, status) VALUES ('BATCH-TRANSIT', 'Rice', 'UNVERIFIED')"
    )

    def block_transit_batch(batch_code):
        assert batch_code == "BATCH-TRANSIT"
        raise HTTPException(status_code=409, detail="Lô hàng đang vận chuyển")

    monkeypatch.setattr(audit_service, "ensure_batch_not_in_transit", block_transit_batch)

    with pytest.raises(HTTPException, match="đang vận chuyển"):
        audit_service.reject_batch(
            db, 1, user_id=4, reason="Không đạt", return_goods=False
        )


@pytest.mark.parametrize(
    ("return_goods", "expected_return_request"),
    [(False, 0), (True, 1)],
)
def test_rejection_notifies_farmer_and_cold_chain_with_return_decision(
    monkeypatch, return_goods, expected_return_request
):
    monkeypatch.delenv("COLD_CHAIN_INTEGRATION_SECRET", raising=False)
    monkeypatch.setattr(audit_service, "ensure_batch_not_in_transit", lambda batch_code: None)
    monkeypatch.setattr(audit_service, "get_latest_batch_report_result", lambda db, batch_id: "FAIL")
    db = _batch_database()
    db.execute(
        """
        CREATE TABLE notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_user_id INTEGER,
            recipient_role TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            batch_id INTEGER,
            notification_type TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        INSERT INTO batches (batch_code, product_name, producer_name, origin, destination,
                             quantity, unit, status, farmer_id)
        VALUES ('BATCH-REJECT', 'Rice', 'Farmer A', 'Nam Dinh', 'Hanoi', 50, 'kg', 'UNVERIFIED', 7)
        """
    )

    result = audit_service.reject_batch(
        db, 1, user_id=4, reason="Thông tin không chính xác", return_goods=return_goods
    )

    assert result["return_goods"] is return_goods
    assert db.execute(
        "SELECT return_goods, return_requested, reason FROM batches WHERE id = 1"
    ).fetchone() == (expected_return_request, expected_return_request, "Thông tin không chính xác")
    notices = db.execute(
        "SELECT recipient_role, notification_type, message FROM notifications ORDER BY id"
    ).fetchall()
    assert [notice[0] for notice in notices] == ["FARMER", "COLD_CHAIN"]
    assert all(notice[1] == ("RETURN_REQUESTED" if return_goods else "BATCH_REJECTED") for notice in notices)
    assert all("Thông tin không chính xác" in notice[2] for notice in notices)
