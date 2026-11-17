import sqlite3
from typing import Any, Optional


def create_notification(
    db: sqlite3.Connection,
    recipient_role: str,
    title: str,
    message: str,
    batch_id: Optional[int] = None,
    recipient_user_id: Optional[int] = None,
    notification_type: str = "GENERAL",
) -> dict[str, Any]:
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO notifications (
            recipient_user_id, recipient_role, title, message, batch_id, notification_type, is_read
        ) VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (recipient_user_id, recipient_role.upper(), title, message, batch_id, notification_type.upper()),
    )
    notification_id = cursor.lastrowid
    db.commit()
    return {
        "id": notification_id,
        "recipient_user_id": recipient_user_id,
        "recipient_role": recipient_role.upper(),
        "title": title,
        "message": message,
        "batch_id": batch_id,
        "notification_type": notification_type.upper(),
        "is_read": False,
    }


def list_notifications(
    db: sqlite3.Connection,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    role_normalized = str(role).strip().upper() if role else ""
    if user_id is not None and role_normalized:
        rows = db.execute(
            """
            SELECT id, recipient_user_id, recipient_role, title, message, batch_id, notification_type, is_read, created_at
            FROM notifications
            WHERE recipient_user_id = ? OR recipient_role = ? OR recipient_role = 'ALL'
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, role_normalized, limit),
        ).fetchall()
    elif user_id is not None:
        rows = db.execute(
            """
            SELECT id, recipient_user_id, recipient_role, title, message, batch_id, notification_type, is_read, created_at
            FROM notifications
            WHERE recipient_user_id = ? OR recipient_role = 'ALL'
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    elif role_normalized:
        rows = db.execute(
            """
            SELECT id, recipient_user_id, recipient_role, title, message, batch_id, notification_type, is_read, created_at
            FROM notifications
            WHERE recipient_role = ? OR recipient_role = 'ALL'
            ORDER BY id DESC
            LIMIT ?
            """,
            (role_normalized, limit),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT id, recipient_user_id, recipient_role, title, message, batch_id, notification_type, is_read, created_at
            FROM notifications
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    columns = [
        "id",
        "recipient_user_id",
        "recipient_role",
        "title",
        "message",
        "batch_id",
        "notification_type",
        "is_read",
        "created_at",
    ]
    result = []
    for row in rows:
        item = dict(zip(columns, row))
        item["is_read"] = bool(item["is_read"])
        result.append(item)
    return result


def count_unread_notifications(
    db: sqlite3.Connection,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
) -> int:
    role_normalized = str(role).strip().upper() if role else ""
    if user_id is not None and role_normalized:
        count = db.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE (recipient_user_id = ? OR recipient_role = ? OR recipient_role = 'ALL')
              AND (is_read = 0 OR is_read IS FALSE)
            """,
            (user_id, role_normalized),
        ).fetchone()[0]
    elif user_id is not None:
        count = db.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE (recipient_user_id = ? OR recipient_role = 'ALL')
              AND (is_read = 0 OR is_read IS FALSE)
            """,
            (user_id,),
        ).fetchone()[0]
    elif role_normalized:
        count = db.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE (recipient_role = ? OR recipient_role = 'ALL')
              AND (is_read = 0 OR is_read IS FALSE)
            """,
            (role_normalized,),
        ).fetchone()[0]
    else:
        count = db.execute(
            "SELECT COUNT(*) FROM notifications WHERE (is_read = 0 OR is_read IS FALSE)"
        ).fetchone()[0]
    return count or 0


def mark_notification_as_read(
    db: sqlite3.Connection,
    notification_id: int,
    user_id: Optional[int] = None,
) -> bool:
    if user_id is not None:
        cursor = db.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ? AND (recipient_user_id = ? OR recipient_user_id IS NULL)",
            (notification_id, user_id),
        )
    else:
        cursor = db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    db.commit()
    return cursor.rowcount > 0


def mark_all_notifications_as_read(
    db: sqlite3.Connection,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
) -> int:
    role_normalized = str(role).strip().upper() if role else ""
    if user_id is not None and role_normalized:
        cursor = db.execute(
            """
            UPDATE notifications SET is_read = 1
            WHERE (recipient_user_id = ? OR recipient_role = ? OR recipient_role = 'ALL')
              AND (is_read = 0 OR is_read IS FALSE)
            """,
            (user_id, role_normalized),
        )
    else:
        cursor = db.execute("UPDATE notifications SET is_read = 1 WHERE (is_read = 0 OR is_read IS FALSE)")
    db.commit()
    return cursor.rowcount
