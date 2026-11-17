import hashlib
import json
import sqlite3

from app.services import blockchain_service
from app.services.audit_trail_service import record_audit_trail


def _audit_database():
    db = sqlite3.connect(":memory:")
    db.execute(
        """
        CREATE TABLE audit_trails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            old_value TEXT,
            new_value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return db


def _configure_blockchain(monkeypatch):
    monkeypatch.setenv("AGRI_BLOCKCHAIN_RPC_URL", "http://localhost:8545")
    monkeypatch.setenv(
        "AGRI_BLOCKCHAIN_CONTRACT_ADDRESS",
        "0x0000000000000000000000000000000000000001",
    )
    monkeypatch.setenv("AGRI_BLOCKCHAIN_PRIVATE_KEY", "test-private-key")


def test_audit_record_does_not_enqueue_when_blockchain_is_not_configured(monkeypatch):
    for name in (
        "AGRI_BLOCKCHAIN_RPC_URL",
        "AGRI_BLOCKCHAIN_CONTRACT_ADDRESS",
        "AGRI_BLOCKCHAIN_PRIVATE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    db = _audit_database()

    record_audit_trail(
        db,
        user_id=7,
        action="CREATE_BATCH",
        entity_type="batch",
        entity_id=12,
    )

    assert db.execute(
        "SELECT id, action FROM audit_trails"
    ).fetchone() == (1, "CREATE_BATCH")
    assert db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'blockchain_anchors'"
    ).fetchone() is None


def test_audit_record_queues_only_canonical_hash_when_blockchain_enabled(monkeypatch):
    _configure_blockchain(monkeypatch)
    db = _audit_database()

    record_audit_trail(
        db,
        user_id=7,
        action="UPLOAD_LAB_REPORT",
        entity_type="lab_report",
        entity_id=12,
        new_value={"file_hash": "private-document-hash"},
    )

    row = db.execute(
        "SELECT event_hash, status FROM blockchain_anchors WHERE audit_id = 1"
    ).fetchone()
    audit = db.execute(
        "SELECT user_id, action, entity_type, entity_id, old_value, new_value, created_at "
        "FROM audit_trails WHERE id = 1"
    ).fetchone()
    canonical_event = json.dumps(
        {
            "audit_id": 1,
            "user_id": 7,
            "action": "UPLOAD_LAB_REPORT",
            "entity_type": "lab_report",
            "entity_id": 12,
            "old_value": None,
            "new_value": '{"file_hash": "private-document-hash"}',
            "created_at": str(audit[6]),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    assert row == (hashlib.sha256(canonical_event.encode("utf-8")).hexdigest(), "PENDING")
    assert "private-document-hash" not in row[0]


def test_blockchain_outbox_retries_then_records_transaction(monkeypatch):
    _configure_blockchain(monkeypatch)
    db = _audit_database()
    record_audit_trail(
        db,
        user_id=7,
        action="APPROVE_BATCH",
        entity_type="batch",
        entity_id=12,
        new_value={"status": "AUDITED"},
    )

    monkeypatch.setattr(
        blockchain_service,
        "_submit_hash",
        lambda event_hash, config: (_ for _ in ()).throw(ConnectionError("RPC unavailable")),
    )
    assert blockchain_service.process_blockchain_outbox(db) == 0
    assert db.execute(
        "SELECT status, attempts, last_error FROM blockchain_anchors WHERE audit_id = 1"
    ).fetchone() == ("PENDING", 1, "RPC unavailable")

    monkeypatch.setattr(
        blockchain_service,
        "_submit_hash",
        lambda event_hash, config: "0xtest",
    )
    monkeypatch.setattr(
        blockchain_service, "_get_transaction_receipt", lambda tx_hash, config: None
    )
    assert blockchain_service.process_blockchain_outbox(db) == 0
    assert db.execute(
        "SELECT status, transaction_hash, attempts FROM blockchain_anchors WHERE audit_id = 1"
    ).fetchone() == ("SUBMITTED", "0xtest", 2)

    monkeypatch.setattr(
        blockchain_service,
        "_get_transaction_receipt",
        lambda tx_hash, config: {"status": 1, "blockNumber": 123},
    )
    assert blockchain_service.process_blockchain_outbox(db) == 1
    assert db.execute(
        "SELECT status, transaction_hash, block_number, attempts, last_error "
        "FROM blockchain_anchors WHERE audit_id = 1"
    ).fetchone() == ("ANCHORED", "0xtest", 123, 2, None)
