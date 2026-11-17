import os
import re
import sqlite3
from pathlib import Path
from typing import Any

import psycopg2


_ID_TABLES = {
    "audit_trails",
    "batches",
    "cold_chain_sync_outbox",
    "businesses",
    "integrity_proofs",
    "lab_reports",
    "notifications",
    "packages",
    "permissions",
    "roles",
    "samples",
    "trace_records",
    "users",
}
SQLITE_DATABASE_PATH = Path(__file__).resolve().parent / "db.db"


def is_postgres_configured() -> bool:
    return bool(os.getenv("AGRI_DATABASE_URL", "").strip())


def connect_sqlite_database():
    connection = sqlite3.connect(SQLITE_DATABASE_PATH, check_same_thread=False)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _rewrite_sql(sql: str, params: tuple[Any, ...] | list[Any]):
    ignore_conflicts = bool(
        re.search(r"\bINSERT\s+OR\s+IGNORE\s+INTO\b", sql, re.IGNORECASE)
    )
    pragma_match = re.fullmatch(r"\s*PRAGMA\s+table_info\((\w+)\)\s*;?\s*", sql, re.IGNORECASE)
    if pragma_match:
        return (
            """
            SELECT ordinal_position - 1, column_name, data_type, 0,
                   column_default, 0
            FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (pragma_match.group(1),),
            False,
        )

    if re.fullmatch(r"\s*PRAGMA\s+(foreign_keys|writable_schema)\s*=\s*(ON|OFF)\s*;?\s*", sql, re.IGNORECASE):
        return "SELECT 1 WHERE FALSE", (), False

    sql = re.sub(
        r"INSERT\s+OR\s+IGNORE\s+INTO",
        "INSERT INTO",
        sql,
        flags=re.IGNORECASE,
    )
    if re.search(r"\bsqlite_master\b", sql, re.IGNORECASE):
        sql = re.sub(r"\bsqlite_master\b", "information_schema.tables", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\btype\s*=\s*'table'\s+AND\s+name\s*=", "table_schema = current_schema() AND table_name =", sql, flags=re.IGNORECASE)
    sql = sql.replace("?", "%s")

    if ignore_conflicts and not re.search(r"\bON\s+CONFLICT\b", sql, re.IGNORECASE):
        sql = sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"

    insert_match = re.match(r"\s*INSERT\s+INTO\s+([a-zA-Z_][\w]*)", sql, re.IGNORECASE)
    add_returning_id = bool(
        insert_match
        and insert_match.group(1).lower() in _ID_TABLES
        and not re.search(r"\bRETURNING\b", sql, re.IGNORECASE)
    )
    if add_returning_id:
        sql = sql.rstrip().rstrip(";") + " RETURNING id"

    return sql, params, add_returning_id


class PostgresCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self._lastrowid = None

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()):
        statement, values, returns_id = _rewrite_sql(sql, params)
        self._cursor.execute(statement, values)
        self._lastrowid = self._cursor.fetchone()[0] if returns_id and self._cursor.rowcount else None
        return self

    def executemany(self, sql: str, seq_of_params):
        statement, _, returns_id = _rewrite_sql(sql, ())
        if returns_id:
            statement = re.sub(r"\s+RETURNING\s+id\s*$", "", statement, flags=re.IGNORECASE)
        self._cursor.executemany(statement, seq_of_params)
        self._lastrowid = None
        return self

    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        self._cursor.close()


class PostgresConnection:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()):
        return self.cursor().execute(sql, params)

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def connect_database() -> PostgresConnection:
    database_url = os.getenv("AGRI_DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError(
            "Set AGRI_DATABASE_URL to the AgriTrace PostgreSQL connection URL."
        )
    return PostgresConnection(
        psycopg2.connect(database_url, connect_timeout=5)
    )


def connect_app_database():
    if is_postgres_configured():
        return connect_database()
    return connect_sqlite_database()
