import re
import sqlite3
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.init_db import (
    create_schema,
    seed_default_role_permissions,
    seed_default_users,
)
from app.database.postgres import connect_database


SQLITE_PATH = BACKEND_ROOT / "app" / "database" / "db.db"
TABLE_ORDER = (
    "roles",
    "permissions",
    "users",
    "businesses",
    "role_permissions",
    "batches",
    "samples",
    "lab_reports",
    "packages",
    "trace_records",
    "audit_trails",
    "integrity_proofs",
)
COLD_CHAIN_TABLES = {"warehouse", "delivery_vehicle", "device", "data"}


def migrate():
    if not SQLITE_PATH.is_file():
        raise FileNotFoundError(f"SQLite source database not found: {SQLITE_PATH}")

    target = connect_database()
    source = None
    try:
        source = sqlite3.connect(SQLITE_PATH)
        source.execute("PRAGMA query_only = ON")
        existing_tables = {
            row[0]
            for row in target.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                """
            ).fetchall()
        }
        cold_tables = existing_tables & COLD_CHAIN_TABLES
        if cold_tables:
            raise RuntimeError(
                "The target database contains Cold Chain tables. "
                "Use a separate, empty PostgreSQL database for AgriTrace."
            )

        create_schema(target)
        nonempty_tables = []
        for table in TABLE_ORDER:
            count = target.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count:
                nonempty_tables.append(table)
        if nonempty_tables:
            raise RuntimeError(
                "The AgriTrace PostgreSQL tables are not empty; migration stopped "
                "to avoid overwriting data. Tables: " + ", ".join(nonempty_tables)
            )

        migrated_counts = {}
        cursor = target.cursor()
        for table in TABLE_ORDER:
            source_columns = [
                row[1] for row in source.execute(f'PRAGMA table_info("{table}")').fetchall()
            ]
            if not source_columns:
                continue
            if any(not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", column) for column in source_columns):
                raise RuntimeError(f"Unexpected column name in SQLite table {table}")

            target_columns = {
                row[0]
                for row in target.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = current_schema() AND table_name = ?
                    """,
                    (table,),
                ).fetchall()
            }
            columns = [column for column in source_columns if column in target_columns]
            if not columns:
                continue

            source_columns_sql = ", ".join('"' + column + '"' for column in columns)
            rows = source.execute(
                f'SELECT {source_columns_sql} FROM "{table}"'
            ).fetchall()
            if not rows:
                migrated_counts[table] = 0
                continue

            names_sql = ", ".join(f'"{column}"' for column in columns)
            placeholders = ", ".join("%s" for _ in columns)
            insert_sql = f'INSERT INTO "{table}" ({names_sql}) VALUES ({placeholders})'
            for row in rows:
                cursor.execute(insert_sql, row)
            migrated_counts[table] = len(rows)

        target.execute(
            """
            UPDATE users
            SET role = CASE UPPER(role)
                WHEN 'CONSUMER' THEN 'PUBLIC'
                ELSE UPPER(role)
            END
            WHERE role IS NOT NULL
            """
        )
        seed_default_role_permissions(target)
        seed_default_users(target)

        for table in TABLE_ORDER:
            if table in {"role_permissions"}:
                continue
            target.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE(MAX(id), 1),
                    COUNT(*) > 0
                )
                FROM "{table}"
                """
            )
        target.commit()
        return migrated_counts
    except Exception:
        target.rollback()
        raise
    finally:
        if source is not None:
            source.close()
        target.close()


if __name__ == "__main__":
    counts = migrate()
    print("SQLite data migrated to AgriTrace PostgreSQL:")
    for table, count in counts.items():
        print(f"  {table}: {count} rows")
    print("Original SQLite database was kept unchanged.")
