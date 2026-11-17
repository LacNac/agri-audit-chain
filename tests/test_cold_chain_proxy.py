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


def test_vehicle_marks_matching_batch_in_transit(monkeypatch):
    monkeypatch.setattr(
        cold_chain_service,
        "get_cold_chain_data",
        lambda endpoint: {
            "success": True,
            "data": [
                {
                    "active_batch_code": "batch-001",
                    "shipment_status": "IN_TRANSIT",
                },
                {
                    "active_batch_code": "BATCH-OTHER",
                    "shipment_status": "IN_TRANSIT",
                },
                {
                    "active_batch_code": "BATCH-002",
                    "shipment_status": "DELIVERED",
                },
            ],
        },
    )

    assert cold_chain_service.is_batch_in_transit("BATCH-001") is True
    assert cold_chain_service.is_batch_in_transit("BATCH-002") is False
