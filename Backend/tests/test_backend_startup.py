import logging
import sqlite3

import pytest

from app.database import init_db


def _sqlite_database_with_required_tables():
    db = sqlite3.connect(":memory:")
    for table in (
        "users",
        "roles",
        "permissions",
        "role_permissions",
        "batches",
        "audit_trails",
    ):
        db.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    return db


def test_backend_startup_uses_sqlite_development_database_without_postgres_url(
    monkeypatch,
    caplog,
):
    db = _sqlite_database_with_required_tables()
    monkeypatch.setattr(init_db, "is_postgres_configured", lambda: False)
    monkeypatch.setattr(init_db, "connect_sqlite_database", lambda: db)
    caplog.set_level(logging.WARNING, logger="app.database.init_db")

    init_db.initialize_database()

    assert "SQLite development database" in caplog.text


def test_backend_startup_explains_missing_sqlite_schema(monkeypatch):
    db = sqlite3.connect(":memory:")
    monkeypatch.setattr(init_db, "is_postgres_configured", lambda: False)
    monkeypatch.setattr(init_db, "connect_sqlite_database", lambda: db)

    with pytest.raises(RuntimeError, match="missing tables"):
        init_db.initialize_database()


def test_sqlite_schema_upgrade_adds_batch_destination_and_sync_outbox():
    db = _sqlite_database_with_required_tables()

    init_db.ensure_schema_upgrades(db)

    batch_columns = {
        row[1] for row in db.execute("PRAGMA table_info(batches)").fetchall()
    }
    outbox_exists = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'cold_chain_sync_outbox'"
    ).fetchone()
    blockchain_table = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'blockchain_anchors'"
    ).fetchone()
    assert "destination" in batch_columns
    assert outbox_exists == (1,)
    assert blockchain_table == (1,)


def test_blockchain_configuration_must_be_complete(monkeypatch):
    from app.services.blockchain_service import validate_blockchain_config

    monkeypatch.setenv("AGRI_BLOCKCHAIN_RPC_URL", "http://localhost:8545")
    monkeypatch.delenv("AGRI_BLOCKCHAIN_CONTRACT_ADDRESS", raising=False)
    monkeypatch.delenv("AGRI_BLOCKCHAIN_PRIVATE_KEY", raising=False)

    with pytest.raises(RuntimeError, match="requires all"):
        validate_blockchain_config()
