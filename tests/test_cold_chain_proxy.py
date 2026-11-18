import json
from urllib.error import URLError

import pytest
from fastapi import HTTPException

from app.services import cold_chain_service


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_cold_chain_proxy_forwards_endpoint_and_query(monkeypatch):
    observed = {}

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        observed["timeout"] = timeout
        return FakeResponse({"success": True, "data": []})

    monkeypatch.setenv("COLD_CHAIN_API_BASE_URL", "http://cold-chain.test/api/")
    monkeypatch.setattr(cold_chain_service, "urlopen", fake_urlopen)

    result = cold_chain_service.get_cold_chain_data(
        "data",
        {"vehicle_id": 7, "page": 2, "unused": None},
    )

    assert result == {"success": True, "data": []}
    assert observed["url"] == "http://cold-chain.test/api/data?vehicle_id=7&page=2"
    assert observed["timeout"] == 5


def test_cold_chain_proxy_defaults_to_render_api(monkeypatch):
    observed = {}

    def fake_urlopen(request, timeout):
        observed["url"] = request.full_url
        return FakeResponse({"success": True, "data": []})

    monkeypatch.delenv("COLD_CHAIN_API_BASE_URL", raising=False)
    monkeypatch.setattr(cold_chain_service, "urlopen", fake_urlopen)

    cold_chain_service.get_cold_chain_data("vehicles")

    assert observed["url"] == (
        "https://cold-chain-telemetry-system-1.onrender.com/api/vehicles"
    )


def test_agri_batches_proxy_authenticates_and_caches_staff_token(monkeypatch):
    observed = {"login_count": 0, "batch_count": 0}
    monkeypatch.setenv("COLD_CHAIN_API_BASE_URL", "http://cold-chain.test/api")
    monkeypatch.setenv("COLD_CHAIN_API_USERNAME", "auditor-reader")
    monkeypatch.setenv("COLD_CHAIN_API_PASSWORD", "test-password")
    monkeypatch.setattr(cold_chain_service, "_cold_chain_staff_token", None)
    monkeypatch.setattr(cold_chain_service, "_cold_chain_staff_token_expires_at", 0)

    def fake_urlopen(request, timeout):
        assert timeout == 5
        if request.full_url.endswith("/auth/login"):
            observed["login_count"] += 1
            assert json.loads(request.data) == {
                "username": "auditor-reader",
                "password": "test-password",
            }
            return FakeResponse(
                {"success": True, "data": {"token": "staff-token"}}
            )

        observed["batch_count"] += 1
        assert request.full_url.endswith("/agri-batches?status=PICKUP_ASSIGNED")
        assert request.get_header("Authorization") == "Bearer staff-token"
        return FakeResponse({"success": True, "data": [{"vehicle_id": 7}]})

    monkeypatch.setattr(cold_chain_service, "urlopen", fake_urlopen)

    first = cold_chain_service.get_cold_chain_agri_batches("PICKUP_ASSIGNED")
    second = cold_chain_service.get_cold_chain_agri_batches("PICKUP_ASSIGNED")

    assert first == second == {"success": True, "data": [{"vehicle_id": 7}]}
    assert observed == {"login_count": 1, "batch_count": 2}


def test_agri_batches_proxy_requires_staff_credentials(monkeypatch):
    monkeypatch.delenv("COLD_CHAIN_API_USERNAME", raising=False)
    monkeypatch.delenv("COLD_CHAIN_API_PASSWORD", raising=False)
    monkeypatch.setattr(cold_chain_service, "_cold_chain_staff_token", None)
    monkeypatch.setattr(cold_chain_service, "_cold_chain_staff_token_expires_at", 0)

    with pytest.raises(HTTPException) as error:
        cold_chain_service.get_cold_chain_agri_batches()

    assert error.value.status_code == 503
    assert "COLD_CHAIN_API_USERNAME" in error.value.detail


def test_cold_chain_proxy_reports_unavailable_upstream(monkeypatch):
    monkeypatch.setattr(
        cold_chain_service,
        "urlopen",
        lambda request, timeout: (_ for _ in ()).throw(URLError("offline")),
    )

    with pytest.raises(HTTPException) as error:
        cold_chain_service.get_cold_chain_data("health")

    assert error.value.status_code == 503
    assert "COLD_CHAIN_API_BASE_URL" in error.value.detail


def test_agri_batch_marks_matching_assigned_batch_in_transit(monkeypatch):
    monkeypatch.setattr(
        cold_chain_service,
        "get_cold_chain_agri_batches",
        lambda: {
            "success": True,
            "data": [
                {
                    "external_batch_code": "batch-001",
                    "vehicle_id": 7,
                    "logistics_status": "PICKUP_ASSIGNED",
                },
                {
                    "external_batch_code": "BATCH-OTHER",
                    "vehicle_id": 8,
                    "logistics_status": "OUT_FOR_DELIVERY",
                },
                {
                    "external_batch_code": "BATCH-002",
                    "vehicle_id": None,
                    "logistics_status": "PICKUP_REQUESTED",
                },
            ],
        },
    )

    assert cold_chain_service.is_batch_in_transit("BATCH-001") is True
    assert cold_chain_service.is_batch_in_transit("BATCH-002") is False
