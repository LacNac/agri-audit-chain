import sqlite3
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
                role TEXT NOT NULL DEFAULT 'farmer',
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
                sample_type TEXT,
                collected_date DATE,
                source_location TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
            );

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

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER,
                user_id INTEGER,
                action TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
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
            ("admin", "Admin", "System administrator"),
            ("farmer", "Farmer", "Producer / farm owner"),
            ("auditor", "Auditor", "Inspection reviewer"),
            ("public", "Public", "Public traceability viewer"),
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
            ("AUDIT_VIEW", "View audit list", "Review audit queue"),
            ("AUDIT_APPROVE", "Approve batch", "Approve audited batch"),
            ("AUDIT_REJECT", "Reject batch", "Reject batch"),
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
            "admin": ["AUTH_LOGIN", "BATCH_CREATE", "BATCH_VIEW_OWN", "BATCH_VIEW_ALL", "AUDIT_VIEW", "AUDIT_APPROVE", "AUDIT_REJECT", "PUBLIC_TRACE_VIEW", "DASHBOARD_VIEW"],
            "farmer": ["AUTH_LOGIN", "BATCH_CREATE", "BATCH_VIEW_OWN"],
            "auditor": ["AUTH_LOGIN", "BATCH_VIEW_ALL", "AUDIT_VIEW", "AUDIT_APPROVE", "AUDIT_REJECT"],
            "public": ["PUBLIC_TRACE_VIEW"],
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
            {"username": "admin", "password": "Admin@123", "full_name": "System Admin", "email": "admin@agriaudit.local", "phone": "0900000001", "role": "admin"},
            {"username": "auditor01", "password": "Auditor@123", "full_name": "Auditor One", "email": "auditor@agriaudit.local", "phone": "0900000002", "role": "auditor"},
            {"username": "farmer01", "password": "Farmer@123", "full_name": "Farmer One", "email": "farmer@agriaudit.local", "phone": "0900000003", "role": "farmer"},
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


def initialize_database() -> None:
    ensure_database_schema()
    seed_default_role_permissions()
    seed_default_users()
