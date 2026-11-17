from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.init_db import initialize_database
from app.database.postgres import connect_app_database, is_postgres_configured


def main():
    initialize_database()
    conn = connect_app_database()
    try:
        if is_postgres_configured():
            rows = conn.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                ORDER BY table_name
                """
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        print(rows)
        for (name,) in rows:
            print(name)
            if is_postgres_configured():
                columns = conn.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = current_schema() AND table_name = ?
                    ORDER BY ordinal_position
                    """,
                    (name,),
                ).fetchall()
            else:
                columns = conn.execute(f"PRAGMA table_info({name})").fetchall()
            print(columns)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
