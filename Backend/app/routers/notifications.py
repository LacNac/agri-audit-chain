from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies.auth import get_current_user, get_db
from ..services.notification_service import (
    count_unread_notifications,
    list_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def get_user_notifications(
    limit: int = Query(50, ge=1, le=200),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    return list_notifications(db, user_id=user["id"], role=user.get("role"), limit=limit)


@router.get("/unread-count")
def get_unread_count(
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    unread = count_unread_notifications(db, user_id=user["id"], role=user.get("role"))
    return {"unread_count": unread}


@router.patch("/{notification_id}/read")
def read_notification(
    notification_id: int,
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    success = mark_notification_as_read(db, notification_id, user_id=user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Thông báo không tồn tại hoặc không thuộc quyền")
    return {"id": notification_id, "is_read": True}


@router.post("/mark-all-read")
def read_all_notifications(
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    updated = mark_all_notifications_as_read(db, user_id=user["id"], role=user.get("role"))
    return {"updated": updated}
