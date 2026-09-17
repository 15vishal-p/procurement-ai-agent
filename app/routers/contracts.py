"""
Endpoints for browsing individual procurement contracts.
"""
from fastapi import APIRouter, Query, HTTPException
from app.db import run_query
from app.models import Contract
from app.config import SNOWFLAKE_TABLE

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=list[Contract])
def list_contracts(
    limit: int = Query(20, ge=1, le=100, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Rows to skip, for pagination"),
    buyer_name: str | None = Query(None, description="Filter by buyer name (partial match)"),
):
    """List contracts, optionally filtered by buyer name, paginated."""
    sql = f"""
        SELECT contract_id, tender_title, buyer_name,
               price_excl_vat, price_incl_vat, announcement_date, contract_status
        FROM {SNOWFLAKE_TABLE}
        WHERE (:buyer_name IS NULL OR buyer_name ILIKE '%' || :buyer_name || '%')
        ORDER BY announcement_date DESC NULLS LAST
        LIMIT :limit OFFSET :offset
    """
    rows = run_query(sql, {"buyer_name": buyer_name, "limit": limit, "offset": offset})
    return rows


@router.get("/{contract_id}", response_model=Contract)
def get_contract(contract_id: str):
    """Get a single contract by its ID."""
    sql = f"""
        SELECT contract_id, tender_title, buyer_name,
               price_excl_vat, price_incl_vat, announcement_date, contract_status
        FROM {SNOWFLAKE_TABLE}
        WHERE contract_id = :contract_id
        LIMIT 1
    """
    rows = run_query(sql, {"contract_id": contract_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Contract not found")
    return rows[0]
