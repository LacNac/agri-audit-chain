from pathlib import Path
import logging
import sqlite3

from app.core.security import hash_password
from app.database.postgres import (
    connect_database,
    connect_sqlite_database,
    is_postgres_configured,
)


SCHEMA_PATH = Path(__file__).with_name("schema_postgres.sql")
logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    ("ADMIN", "Admin", "System administrator"),
    ("FARMER", "Farmer", "Producer / farm owner"),
    ("AUDITOR", "Auditor", "Inspection reviewer"),
    ("COLD_CHAIN", "Cold Chain", "Cold chain logistics and warehouse operator"),
    ("PUBLIC", "Public", "Public traceability viewer"),
]

DEFAULT_PERMISSIONS = [
    ("AUTH_LOGIN", "Login", "User login"),
    ("USER_VIEW", "View users", "View user accounts"),
    ("USER_CREATE", "Create users", "Create user accounts"),
    ("USER_UPDATE", "Update users", "Update user accounts"),
    ("ROLE_VIEW", "View roles", "View roles and permissions"),
    ("ROLE_UPDATE", "Update roles", "Assign user roles"),
    ("BATCH_CREATE", "Create Batch", "Create new batch"),
    ("BATCH_VIEW_OWN", "View own batches", "View own produced batches"),
    ("BATCH_VIEW_ALL", "View all batches", "View all batches for auditor/admin"),
    ("BATCH_UPDATE_OWN", "Update own batch", "Update own batch before audit"),
    ("BATCH_DELETE_OWN", "Delete own batch", "Delete own unverified batch"),
    ("SAMPLE_CREATE", "Create Sample", "Create sample linked to a batch"),
    ("SAMPLE_VIEW_OWN", "View own samples", "View samples belonging to own batches"),
    ("SAMPLE_VIEW_ALL", "View all samples", "View all samples"),
    ("AUDIT_VIEW", "View audit list", "Review audit queue"),
    ("AUDIT_UPLOAD_REPORT", "Upload lab report", "Upload laboratory test report"),
    ("AUDIT_APPROVE", "Approve batch", "Approve audited batch"),
    ("AUDIT_REJECT", "Reject batch", "Reject batch"),
    ("AUDIT_VIEW_HISTORY", "View audit history", "View audit trail"),
    ("HASH_VERIFY", "Verify report hash", "Verify report file integrity"),
    ("PROOF_VIEW", "View integrity proof", "View proof of integrity"),
    ("QR_GENERATE", "Generate QR", "Generate QR for audited batch"),
    ("PUBLIC_TRACE_VIEW", "Public trace view", "Public traceability access"),
    ("DASHBOARD_VIEW", "Dashboard view", "Admin dashboard access"),
    ("NOTIFICATION_VIEW", "View notifications", "View role notifications"),
]

ROLE_PERMISSION_MAP = {
    "ADMIN": [
        "AUTH_LOGIN", "USER_VIEW", "USER_CREATE", "USER_UPDATE", "ROLE_VIEW",
        "ROLE_UPDATE", "DASHBOARD_VIEW", "AUDIT_VIEW_HISTORY", "NOTIFICATION_VIEW",
    ],
    "FARMER": [
        "AUTH_LOGIN", "BATCH_CREATE", "BATCH_VIEW_OWN", "BATCH_UPDATE_OWN",
        "BATCH_DELETE_OWN", "SAMPLE_VIEW_OWN", "QR_GENERATE", "NOTIFICATION_VIEW",
    ],
    "AUDITOR": [
        "AUTH_LOGIN", "BATCH_VIEW_ALL", "SAMPLE_CREATE", "SAMPLE_VIEW_ALL",
        "AUDIT_VIEW", "AUDIT_UPLOAD_REPORT", "AUDIT_APPROVE", "AUDIT_REJECT",
        "AUDIT_VIEW_HISTORY", "HASH_VERIFY", "PROOF_VIEW", "QR_GENERATE", "NOTIFICATION_VIEW",
    ],
    "COLD_CHAIN": [
        "AUTH_LOGIN", "BATCH_VIEW_ALL", "NOTIFICATION_VIEW",
    ],
    "PUBLIC": ["PUBLIC_TRACE_VIEW"],
}

DEFAULT_USERS = [
    {"username": "hanglt", "password": "Admin@123", "full_name": "Lê Thu Hằng", "email": "hanglt@gmail.com", "role": "ADMIN"},
    {"username": "dieult", "password": "Admin@234", "full_name": "Lê Thị Diệu", "email": "dieult@gamil.com", "role": "ADMIN"},
    {"username": "huyenhtk", "password": "Farmer@123", "full_name": "Hàn Thị Khánh Huyền", "email": "huyenhtk@gmail.com", "role": "FARMER"},
    {"username": "haidn", "password": "Farmer@234", "full_name": "Đặng Nhật Hải", "email": "haidn@gmail.com", "role": "FARMER"},
    {"username": "giangbh", "password": "Auditor@123", "full_name": "Bùi Hương Giang", "email": "giangbh@gmail.com", "role": "AUDITOR"},
    {"username": "dathx", "password": "Auditor@234", "full_name": "Hoàng Xuân Đạt", "email": "dathx@gmail.com", "role": "AUDITOR"},
    {"username": "kholanh", "password": "ColdChain@123", "full_name": "Công ty TNHH Kho Lạnh Miền Bắc", "email": "kholanh@gmail.com", "role": "COLD_CHAIN"},
]


def ensure_schema_upgrades(db):
    cols_query = db.execute("PRAGMA table_info(batches)").fetchall()
    existing_cols = {row[1] for row in cols_query}

    is_sqlite = isinstance(db, sqlite3.Connection)

    if is_sqlite or existing_cols:
        if "return_goods" not in existing_cols:
            db.execute("ALTER TABLE batches ADD COLUMN return_goods INTEGER DEFAULT 0")
        if "rejected_at" not in existing_cols:
            db.execute("ALTER TABLE batches ADD COLUMN rejected_at DATETIME")
        if "return_requested" not in existing_cols:
            db.execute("ALTER TABLE batches ADD COLUMN return_requested INTEGER DEFAULT 0")
        if "destination" not in existing_cols:
            db.execute("ALTER TABLE batches ADD COLUMN destination TEXT")

        db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
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
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced_at DATETIME,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_anchors (
                audit_id INTEGER PRIMARY KEY,
                event_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'PENDING',
                transaction_hash TEXT,
                block_number BIGINT,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                anchored_at DATETIME
            )
        """)
        db.commit()
    else:
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS return_goods BOOLEAN DEFAULT FALSE")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP WITHOUT TIME ZONE")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS return_requested BOOLEAN DEFAULT FALSE")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS destination TEXT")
        db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                recipient_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                recipient_role TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                batch_id INTEGER REFERENCES batches(id) ON DELETE CASCADE,
                notification_type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS cold_chain_sync_outbox (
                id SERIAL PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP WITHOUT TIME ZONE,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_anchors (
                audit_id INTEGER PRIMARY KEY,
                event_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'PENDING',
                transaction_hash TEXT,
                block_number BIGINT,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                anchored_at TIMESTAMP WITHOUT TIME ZONE
            )
        """)
        db.commit()


def create_schema(db=None):
    owns_connection = db is None
    db = db or connect_database()
    try:
        for statement in SCHEMA_PATH.read_text(encoding="utf-8").split(";"):
            if statement.strip():
                db.execute(statement)
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS product_type TEXT")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS note TEXT")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS reason TEXT")
        db.execute("ALTER TABLE batches ADD COLUMN IF NOT EXISTS destination TEXT")
        db.commit()
        ensure_schema_upgrades(db)
    finally:
        if owns_connection:
            db.close()


def seed_default_role_permissions(db):
    for code, name, description in DEFAULT_ROLES:
        db.execute(
            "INSERT INTO roles (code, name, description) VALUES (?, ?, ?) ON CONFLICT(code) DO NOTHING",
            (code, name, description),
        )

    for code, name, description in DEFAULT_PERMISSIONS:
        db.execute(
            "INSERT INTO permissions (code, name, description) VALUES (?, ?, ?) ON CONFLICT(code) DO NOTHING",
            (code, name, description),
        )

    for role_code, permission_codes in ROLE_PERMISSION_MAP.items():
        role = db.execute("SELECT id FROM roles WHERE code = ?", (role_code,)).fetchone()
        if not role:
            continue
        for permission_code in permission_codes:
            permission = db.execute(
                "SELECT id FROM permissions WHERE code = ?",
                (permission_code,),
            ).fetchone()
            if permission:
                db.execute(
                    """
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (?, ?)
                    ON CONFLICT(role_id, permission_id) DO NOTHING
                    """,
                    (role[0], permission[0]),
                )


def seed_default_users(db):
    for user in DEFAULT_USERS:
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user["username"], user["email"]),
        ).fetchone()
        if existing:
            continue
        db.execute(
            """
            INSERT INTO users (username, password_hash, full_name, email, phone, role, status)
            VALUES (?, ?, ?, ?, '', ?, 'active')
            """,
            (
                user["username"],
                hash_password(user["password"]),
                user["full_name"],
                user["email"],
                user["role"],
            ),
        )


def initialize_database():
    if not is_postgres_configured():
        db = connect_sqlite_database()
        try:
            existing_tables = {
                row[0]
                for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            required_tables = {
                "users",
                "roles",
                "permissions",
                "role_permissions",
                "batches",
                "audit_trails",
            }
            missing_tables = required_tables - existing_tables
            if missing_tables:
                raise RuntimeError(
                    "SQLite development database is missing tables: "
                    + ", ".join(sorted(missing_tables))
                    + ". Configure AGRI_DATABASE_URL to use PostgreSQL."
                )
            ensure_schema_upgrades(db)
            db.commit()
        finally:
            db.close()
        logger.warning(
            "AGRI_DATABASE_URL is not set; AgriTrace is using its SQLite "
            "development database. Set AGRI_DATABASE_URL to use PostgreSQL."
        )
        return

    db = connect_database()
    try:
        cold_chain_tables = {
            row[0]
            for row in db.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                """
            ).fetchall()
        } & {"warehouse", "delivery_vehicle", "device"}
        if cold_chain_tables:
            raise RuntimeError(
                "AGRI_DATABASE_URL points to a Cold Chain database. "
                "Use a separate PostgreSQL database for AgriTrace."
            )
        create_schema(db)
        db.execute(
            """
            UPDATE users
            SET role = CASE UPPER(role)
                WHEN 'CONSUMER' THEN 'PUBLIC'
                ELSE UPPER(role)
            END
            WHERE role IS NOT NULL
            """
        )
        seed_default_role_permissions(db)
        seed_default_users(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    print("AgriTrace PostgreSQL database initialized.")
