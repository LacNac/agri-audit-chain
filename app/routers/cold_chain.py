from fastapi import APIRouter, Depends, Query

from ..dependencies.rbac import require_permission
from ..services.cold_chain_service import get_cold_chain_data

router = APIRouter(
    prefix="/cold-chain",
    tags=["cold-chain"],
    dependencies=[Depends(require_permission("AUDIT_VIEW"))],
)


@router.get("/health")
def cold_chain_health():
    return get_cold_chain_data("health")


@router.get("/warehouses")
def list_cold_chain_warehouses(
    status: str | None = None,
    search: str | None = None,
):
    return get_cold_chain_data("warehouses", {"status": status, "search": search})


@router.get("/warehouses/{warehouse_id}")
def get_cold_chain_warehouse(warehouse_id: int):
    return get_cold_chain_data(f"warehouses/{warehouse_id}")


@router.get("/vehicles")
def list_cold_chain_vehicles(
    status: str | None = None,
    warehouse_id: int | None = None,
    search: str | None = None,
):
    return get_cold_chain_data(
        "vehicles",
        {"status": status, "warehouse_id": warehouse_id, "search": search},
    )


@router.get("/vehicles/{vehicle_id}")
def get_cold_chain_vehicle(vehicle_id: int):
    return get_cold_chain_data(f"vehicles/{vehicle_id}")


@router.get("/telemetry")
def list_cold_chain_telemetry(
    device_id: int | None = None,
    warehouse_id: int | None = None,
    vehicle_id: int | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=500),
):
    return get_cold_chain_data(
        "data",
        {
            "device_id": device_id,
            "warehouse_id": warehouse_id,
            "vehicle_id": vehicle_id,
            "page": page,
            "limit": limit,
        },
    )


@router.get("/telemetry/device/{device_id}")
def get_cold_chain_device_telemetry(
    device_id: int,
    limit: int = Query(50, ge=1, le=500),
):
    return get_cold_chain_data(f"data/device/{device_id}", {"limit": limit})
