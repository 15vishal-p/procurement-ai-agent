"""
Endpoints for buyer-level spend analysis.
"""
from fastapi import APIRouter, Query
from app.db import run_query
from app.models import BuyerSpend
from app.config import SNOWFLAKE_TABLE

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.get("/top", response_model=list[BuyerSpend])
def top_buyers(
    n: int = Query(10, ge=1, le=50, description="Number of top buyers to return"),
):
    """Top N buyers ranked by total contract value."""
    sql = f"""
        SELECT buyer_name,
               SUM(price_excl_vat) AS total_spend,
               COUNT(*) AS contract_count
        FROM {SNOWFLAKE_TABLE}
        WHERE buyer_name IS NOT NULL AND price_excl_vat IS NOT NULL
        GROUP BY buyer_name
        ORDER BY total_spend DESC
        LIMIT :n
    """
    return run_query(sql, {"n": n})
