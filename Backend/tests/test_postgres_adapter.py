from app.database.postgres import PostgresCursor, _rewrite_sql


def test_rewrite_sql_adds_postgres_returning_for_generated_ids():
    sql, params, returns_id = _rewrite_sql(
        "INSERT INTO batches (batch_code) VALUES (?)",
        ("BATCH-1",),
    )

    assert sql == "INSERT INTO batches (batch_code) VALUES (%s) RETURNING id"
    assert params == ("BATCH-1",)
    assert returns_id


def test_rewrite_sql_preserves_ignore_conflict_behavior():
    sql, params, returns_id = _rewrite_sql(
        "INSERT OR IGNORE INTO roles (code) VALUES (?)",
        ("AUDITOR",),
    )

    assert sql == "INSERT INTO roles (code) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id"
    assert params == ("AUDITOR",)
    assert returns_id


def test_rewrite_sql_maps_pragma_table_info_to_postgres_catalog():
    sql, params, returns_id = _rewrite_sql("PRAGMA table_info(batches)", ())

    assert "information_schema.columns" in sql
    assert params == ("batches",)
    assert not returns_id


def test_rewrite_sql_maps_sqlite_table_lookup_to_postgres_catalog():
    sql, params, returns_id = _rewrite_sql(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        ("batches",),
    )

    assert "information_schema.tables" in sql
    assert "table_schema = current_schema()" in sql
    assert "table_name = %s" in sql
    assert params == ("batches",)
    assert not returns_id


class FakeCursor:
    def __init__(self):
        self.rowcount = 0
        self.statement = None
        self.rows = []

    def execute(self, statement, params):
        self.statement = statement
        self.rowcount = 1
        self.rows = [(42,)] if "RETURNING id" in statement else []

    def executemany(self, statement, rows):
        self.statement = statement

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None


def test_postgres_cursor_preserves_lastrowid_for_sqlite_style_callers():
    cursor = PostgresCursor(FakeCursor())

    cursor.execute("INSERT INTO batches (batch_code) VALUES (?)", ("BATCH-1",))

    assert cursor.lastrowid == 42
