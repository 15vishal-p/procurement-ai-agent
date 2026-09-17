"""
Database access layer. Uses SQLAlchemy core with plain SQL text queries -
deliberately avoids ORM-style table reflection, which has known rough edges
with the Snowflake dialect (see the ETL project's load.py for the story).
"""
from sqlalchemy import create_engine, text
from app.config import get_db_url

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_db_url(), pool_pre_ping=True)
    return _engine


def run_query(sql: str, params: dict | None = None) -> list[dict]:
    """Runs a parameterized SELECT and returns rows as a list of dicts."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]
