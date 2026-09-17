"""
Endpoint for high-level dataset statistics.
"""
from fastapi import APIRouter
from app.db import run_query
from app.models import StatsSummary
from app.config import SNOWFLAKE_TABLE

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def summary():
    """Overall summary stats for the whole dataset."""
    sql = f"""
        SELECT
            COUNT(*) AS total_contracts,
            SUM(price_excl_vat) AS total_value,
            COUNT(DISTINCT buyer_name) AS unique_buyers,
            MIN(announcement_date) AS date_range_start,
            MAX(announcement_date) AS date_range_end
        FROM {SNOWFLAKE_TABLE}
    """
    rows = run_query(sql)
    return rows[0]
