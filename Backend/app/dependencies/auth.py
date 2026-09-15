
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "db.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()