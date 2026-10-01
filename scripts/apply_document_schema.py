import sqlite3
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.init_db import ensure_database_schema


def main():
    ensure_database_schema()
    db_path = BACKEND_ROOT / "app" / "database" / "db.db"
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        print(rows)
        for (name,) in rows:
            print(name)
            print(conn.execute(f"PRAGMA table_info({name})").fetchall())
    finally:
        conn.close()


if __name__ == "__main__":
    main()
