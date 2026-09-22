import sqlite3
import json
from pathlib import Path

from ..core.security import hash_password

DB_PATH = Path(__file__).resolve().parent / "db.db"


def ensure_database_schema() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                role TEXT NOT NULL DEFAULT 'FARMER',
                status TEXT NOT NULL DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                business_name TEXT,
                business_type TEXT,
                product_type TEXT,
                tax_code TEXT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_code TEXT NOT NULL UNIQUE,
                product_name TEXT NOT NULL,
                producer_name TEXT NOT NULL,
                origin TEXT,
                quantity REAL,
                unit TEXT,
                production_date DATE,
                expiry_date DATE,
                status TEXT NOT NULL DEFAULT 'UNVERIFIED',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                farmer_id INTEGER,
                FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_code TEXT NOT NULL UNIQUE,
                batch_id INTEGER NOT NULL,
                sampling_date DATE,
                sample_quantity REAL,
                sample_unit TEXT,
                sampling_location TEXT,
                sampling_method TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_samples_one_per_batch
                ON samples(batch_id);

            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_code TEXT NOT NULL UNIQUE,
                sample_id INTEGER NOT NULL,
                batch_id INTEGER NOT NULL,
                lab_name TEXT,
                lab_code TEXT,
                report_date DATE,
                result TEXT,
                file_name TEXT,
                file_hash TEXT,
                file_path TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_trails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                old_value TEXT,
                new_value TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_code TEXT NOT NULL UNIQUE,
                batch_id INTEGER NOT NULL,
                quantity REAL,
                unit TEXT,
                qr_code TEXT,
                trace_id TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS trace_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                package_id INTEGER,
                trace_id TEXT NOT NULL,
                public_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE SET NULL
            );
            """
        )

        default_roles = [
            ("ADMIN", "Admin", "System administrator"),
            ("FARMER", "Farmer", "Producer / farm owner"),
            ("AUDITOR", "Auditor", "Inspection reviewer"),
            ("PUBLIC", "Public", "Public traceability viewer"),
        ]

        for code, name, description in default_roles:
            conn.execute(
                "INSERT OR IGNORE INTO roles (code, name, description) VALUES (?, ?, ?)",
                (code, name, description),
            )

        default_permissions = [
            ("AUTH_LOGIN", "Login", "User login"),
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
            ("QR_GENERATE", "Generate QR", "Generate QR for audited batch"),
            ("PUBLIC_TRACE_VIEW", "Public trace view", "Public traceability access"),
            ("DASHBOARD_VIEW", "Dashboard view", "Admin dashboard access"),
        ]

        for code, name, description in default_permissions:
            conn.execute(
                "INSERT OR IGNORE INTO permissions (code, name, description) VALUES (?, ?, ?)",
                (code, name, description),
            )

        conn.commit()
    finally:
        conn.close()


def seed_default_role_permissions() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        role_permission_map = {
            "ADMIN": ["AUTH_LOGIN", "BATCH_CREATE", "BATCH_VIEW_OWN", "BATCH_VIEW_ALL", "BATCH_UPDATE_OWN", "BATCH_DELETE_OWN", "SAMPLE_CREATE", "SAMPLE_VIEW_OWN", "SAMPLE_VIEW_ALL", "AUDIT_VIEW", "AUDIT_UPLOAD_REPORT", "AUDIT_APPROVE", "AUDIT_REJECT", "AUDIT_VIEW_HISTORY", "QR_GENERATE", "PUBLIC_TRACE_VIEW", "DASHBOARD_VIEW"],
            "FARMER": ["AUTH_LOGIN", "BATCH_CREATE", "BATCH_VIEW_OWN", "BATCH_UPDATE_OWN", "BATCH_DELETE_OWN", "SAMPLE_VIEW_OWN", "QR_GENERATE"],
            "AUDITOR": ["AUTH_LOGIN", "BATCH_VIEW_ALL", "SAMPLE_CREATE", "SAMPLE_VIEW_ALL", "AUDIT_VIEW", "AUDIT_UPLOAD_REPORT", "AUDIT_APPROVE", "AUDIT_REJECT", "AUDIT_VIEW_HISTORY"],
            "PUBLIC": ["PUBLIC_TRACE_VIEW"],
        }

        for role_code, permission_codes in role_permission_map.items():
            role_row = conn.execute("SELECT id FROM roles WHERE code = ?", (role_code,)).fetchone()
            if not role_row:
                continue
            role_id = role_row[0]

            for permission_code in permission_codes:
                perm_row = conn.execute("SELECT id FROM permissions WHERE code = ?", (permission_code,)).fetchone()
                if not perm_row:
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)",
                    (role_id, perm_row[0]),
                )

        conn.commit()
    finally:
        conn.close()


def seed_default_users() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        default_users = [
            {"username": "hanglt", "password": "Admin@123", "full_name": "Lê Thu Hằng", "email": "hanglt@gmail.com", "phone": "", "role": "ADMIN"},
            {"username": "dieult", "password": "Admin@234", "full_name": "Lê Thị Diệu", "email": "dieult@gamil.com", "phone": "", "role": "ADMIN"},
            {"username": "huyenhtk", "password": "Farmer@123", "full_name": "Hàn Thị Khánh Huyền", "email": "huyenhtk@gmail.com", "phone": "", "role": "FARMER"},
            {"username": "haidn", "password": "Farmer@234", "full_name": "Đặng Nhật Hải", "email": "haidn@gmail.com", "phone": "", "role": "FARMER"},
            {"username": "giangbh", "password": "Auditor@123", "full_name": "Bùi Hương Giang", "email": "giangbh@gmail.com", "phone": "", "role": "AUDITOR"},
            {"username": "dathx", "password": "Auditor@234", "full_name": "Hoàng Xuân Đạt", "email": "dathx@gmail.com", "phone": "", "role": "AUDITOR"},
        ]

        for user in default_users:
            existing = conn.execute(
                "SELECT id, password_hash FROM users WHERE username = ? OR email = ?",
                (user["username"], user["email"]),
            ).fetchone()
            if existing:
                if len(existing[1]) != 64:
                    conn.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (hash_password(user["password"]), existing[0]),
                    )
                continue
            conn.execute(
                """
                INSERT INTO users (username, password_hash, full_name, email, phone, role, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
                """,
                (
                    user["username"],
                    hash_password(user["password"]),
                    user["full_name"],
                    user["email"],
                    user["phone"],
                    user["role"],
                ),
            )

        conn.commit()
    finally:
        conn.close()


def migrate_legacy_users_schema() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        row = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'users'").fetchone()
        if row and "CHECK(\"role\" IN ('admin', 'auditor', 'farmer', 'consumer'))" in row[0]:
            conn.execute("ALTER TABLE users RENAME TO users_legacy")
            conn.execute(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'FARMER', 'AUDITOR', 'PUBLIC')),
                    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'locked')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                INSERT INTO users (id, username, password_hash, full_name, email, phone, role, status, created_at)
                  SELECT id, username, password_hash, full_name, email, phone,
                      CASE UPPER(role) WHEN 'CONSUMER' THEN 'PUBLIC' ELSE UPPER(role) END,
                      status, created_at
                FROM users_legacy
                """
            )
            conn.execute("DROP TABLE users_legacy")
            conn.commit()
    finally:
        conn.close()


def repair_businesses_user_foreign_key() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        foreign_keys = conn.execute("PRAGMA foreign_key_list(businesses)").fetchall()
        if not foreign_keys or foreign_keys[0][2] != "users_legacy":
            return

        conn.execute("ALTER TABLE businesses RENAME TO businesses_legacy")
        conn.execute(
            """
            CREATE TABLE businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                business_name TEXT,
                business_type TEXT,
                product_type TEXT,
                tax_code TEXT UNIQUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO businesses (id, user_id, business_name, business_type, product_type, tax_code)
            SELECT id, user_id, business_name, business_type, product_type, tax_code
            FROM businesses_legacy
            """
        )
        conn.execute("DROP TABLE businesses_legacy")
        conn.commit()
    finally:
        conn.close()


def ensure_batch_columns() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(batches)").fetchall()]
        if "producer_name" not in columns:
            conn.execute("ALTER TABLE batches ADD COLUMN producer_name TEXT")
        if "farmer_id" not in columns:
            conn.execute("ALTER TABLE batches ADD COLUMN farmer_id INTEGER")
        if "product_type" not in columns:
            conn.execute("ALTER TABLE batches ADD COLUMN product_type TEXT")
        if "note" not in columns:
            conn.execute("ALTER TABLE batches ADD COLUMN note TEXT")
        conn.commit()
    finally:
        conn.close()


def migrate_batch_status_schema() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        schema = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'batches'"
        ).fetchone()
        if not schema or "UNVERIFIED" in schema[0]:
            return

        conn.execute(
            """
            CREATE TABLE batches_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_code TEXT NOT NULL UNIQUE,
                product_name TEXT NOT NULL,
                product_type TEXT,
                producer_name TEXT NOT NULL,
                origin TEXT NOT NULL,
                quantity REAL NOT NULL CHECK (quantity > 0),
                unit TEXT NOT NULL,
                production_date DATE,
                expiry_date DATE,
                status TEXT NOT NULL DEFAULT 'UNVERIFIED'
                    CHECK (status IN ('UNVERIFIED', 'AUDITED', 'REJECTED')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                farmer_id INTEGER,
                note TEXT,
                FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO batches_new
            (id, batch_code, product_name, product_type, producer_name, origin,
             quantity, unit, production_date, expiry_date, status, created_at,
             farmer_id, note)
            SELECT id, batch_code, product_name, product_type,
                   COALESCE(producer_name, 'Chưa xác định'),
                   COALESCE(origin, 'Chưa xác định'),
                   quantity, unit, production_date, expiry_date,
                   CASE status
                       WHEN 'passed' THEN 'AUDITED'
                       WHEN 'inspected' THEN 'AUDITED'
                       WHEN 'failed' THEN 'REJECTED'
                       ELSE 'UNVERIFIED'
                   END,
                   created_at, farmer_id, note
            FROM batches_legacy
            """
        )
        conn.execute("DROP TABLE batches")
        conn.execute("ALTER TABLE batches_new RENAME TO batches")
        conn.commit()
    finally:
        conn.close()


def repair_legacy_foreign_key_references() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA writable_schema = ON")
    try:
        conn.execute(
            """
            UPDATE sqlite_master
            SET sql = REPLACE(REPLACE(sql, '"batches_legacy"', 'batches'), '"users_legacy"', 'users')
                        WHERE type = 'table'
                            AND name NOT IN ('batches_legacy', 'users_legacy')
                            AND sql IS NOT NULL
            """
        )
        version = conn.execute("PRAGMA schema_version").fetchone()[0]
        conn.execute(f"PRAGMA schema_version = {version + 1}")
        conn.commit()
    finally:
        conn.execute("PRAGMA writable_schema = OFF")
        conn.close()


def ensure_sample_columns() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        sample_columns = [row[1] for row in conn.execute("PRAGMA table_info(samples)").fetchall()]
        if "sampling_date" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sampling_date DATE")
        if "sample_quantity" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sample_quantity REAL")
        if "sample_unit" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sample_unit TEXT")
        if "sampling_location" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sampling_location TEXT")
        if "sampling_method" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sampling_method TEXT")
        if "sample_code" not in sample_columns:
            conn.execute("ALTER TABLE samples ADD COLUMN sample_code TEXT")
        conn.commit()
    finally:
        conn.close()


def migrate_sample_history_to_audit_trails() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sample_history'"
        ).fetchone()
        if not exists:
            return

        rows = conn.execute(
            "SELECT sample_id, action, details, created_at FROM sample_history ORDER BY id"
        ).fetchall()
        for sample_id, action, details, created_at in rows:
            conn.execute(
                """
                INSERT INTO audit_trails
                    (user_id, action, entity_type, entity_id, old_value, new_value, created_at)
                VALUES (NULL, ?, 'sample', ?, NULL, ?, ?)
                """,
                (action.upper(), sample_id, json.dumps({"details": details}, ensure_ascii=False), created_at),
            )
        conn.execute("DROP TABLE sample_history")
        conn.commit()
    finally:
        conn.close()


def migrate_audit_logs_to_trails() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        audit_logs_exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'audit_logs'"
        ).fetchone()
        if not audit_logs_exists:
            return

        rows = conn.execute(
            """
            SELECT batch_id, user_id, action, previous_status, new_status, reason, created_at
            FROM audit_logs
            ORDER BY id
            """
        ).fetchall()
        for batch_id, user_id, action, previous_status, new_status, reason, created_at in rows:
            if batch_id is None:
                continue
            conn.execute(
                """
                INSERT INTO audit_trails
                    (user_id, action, entity_type, entity_id, old_value, new_value, created_at)
                VALUES (?, ?, 'batch', ?, ?, ?, ?)
                """,
                (
                    user_id,
                    "APPROVE_BATCH" if action == "APPROVE" else "REJECT_BATCH",
                    batch_id,
                    json.dumps({"status": previous_status}, ensure_ascii=False),
                    json.dumps({"status": new_status, "reason": reason}, ensure_ascii=False),
                    created_at,
                ),
            )
        conn.execute("DROP TABLE audit_logs")
        conn.commit()
    finally:
        conn.close()


def normalize_role_values() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("DELETE FROM role_permissions")
        conn.execute("DELETE FROM roles")
        conn.execute("DELETE FROM permissions")

        default_roles = [
            ("ADMIN", "Admin", "System administrator"),
            ("FARMER", "Farmer", "Producer / farm owner"),
            ("AUDITOR", "Auditor", "Inspection reviewer"),
            ("PUBLIC", "Public", "Public traceability viewer"),
        ]
        for code, name, description in default_roles:
            conn.execute(
                "INSERT INTO roles (code, name, description) VALUES (?, ?, ?)",
                (code, name, description),
            )

        default_permissions = [
            ("AUTH_LOGIN", "Login", "User login"),
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
            ("QR_GENERATE", "Generate QR", "Generate QR for audited batch"),
            ("PUBLIC_TRACE_VIEW", "Public trace view", "Public traceability access"),
            ("DASHBOARD_VIEW", "Dashboard view", "Admin dashboard access"),
        ]
        for code, name, description in default_permissions:
            conn.execute(
                "INSERT INTO permissions (code, name, description) VALUES (?, ?, ?)",
                (code, name, description),
            )

        conn.execute("UPDATE users SET role = UPPER(role) WHERE role IS NOT NULL")
        conn.commit()
    finally:
        conn.close()


def initialize_database() -> None:
    ensure_database_schema()
    ensure_batch_columns()
    migrate_batch_status_schema()
    repair_legacy_foreign_key_references()
    ensure_sample_columns()
    migrate_legacy_users_schema()
    repair_businesses_user_foreign_key()
    normalize_role_values()
    migrate_sample_history_to_audit_trails()
    migrate_audit_logs_to_trails()
    seed_default_role_permissions()
    seed_default_users()
