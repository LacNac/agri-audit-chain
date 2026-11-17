import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.dependencies.auth import get_db
from app.routers.integration import router


@pytest.fixture
def integration_client(monkeypatch):
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute(
        """
        CREATE TABLE batches (
            id INTEGER PRIMARY KEY,
            batch_code TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            product_type TEXT,
            producer_name TEXT,
            origin TEXT,
            destination TEXT,
            quantity REAL,
            unit TEXT,
            status TEXT NOT NULL,
            reason TEXT,
            return_goods INTEGER DEFAULT 0,
            return_requested INTEGER DEFAULT 0
        )
        """
    )
    db.executemany(
        """
        INSERT INTO batches (
            id, batch_code, product_name, product_type, producer_name, origin,
            destination, quantity, unit, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "BATCH-APPROVED", "Táo", "Trái cây", "Nhà vườn A", "Đà Lạt", "Hà Nội", 100, "kg", "AUDITED"),
            (2, "BATCH-PENDING", "Cam", "Trái cây", "Nhà vườn B", "Vĩnh Long", "Hồ Chí Minh", 50, "kg", "UNVERIFIED"),
        ],
    )

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setenv("COLD_CHAIN_INTEGRATION_SECRET", "test-shared-key")

    with TestClient(app) as client:
        yield client
    db.close()


def test_carrier_lists_only_approved_batches(integration_client):
    response = integration_client.get(
        "/integration/batches",
        headers={"X-Integration-Key": "test-shared-key"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert [batch["batch_code"] for batch in payload["data"]] == ["BATCH-APPROVED"]
    assert payload["data"][0]["destination"] == "Hà Nội"


def test_carrier_fetches_approved_batch_by_code(integration_client):
    response = integration_client.get(
        "/integration/batches/BATCH-APPROVED",
        headers={"X-Integration-Key": "test-shared-key"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["agri_batch_id"] == 1


def test_carrier_cannot_fetch_unapproved_batch(integration_client):
    response = integration_client.get(
        "/integration/batches/BATCH-PENDING",
        headers={"X-Integration-Key": "test-shared-key"},
    )

    assert response.status_code == 409


def test_carrier_api_requires_shared_integration_key(integration_client):
    response = integration_client.get("/integration/batches")

    assert response.status_code == 401


def test_carrier_api_fails_explicitly_when_integration_key_is_not_configured(
    integration_client, monkeypatch
):
    monkeypatch.delenv("COLD_CHAIN_INTEGRATION_SECRET")

    response = integration_client.get(
        "/integration/batches",
        headers={"X-Integration-Key": "test-shared-key"},
    )

    assert response.status_code == 503
