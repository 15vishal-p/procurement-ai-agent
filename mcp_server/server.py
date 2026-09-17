
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from app.db import run_query
from app.config import SNOWFLAKE_TABLE

mcp = FastMCP("Procurement Data Server")


@mcp.tool()
def search_contracts(buyer_name: str = None, limit: int = 20) -> list[dict]:
    
    limit = min(max(limit, 1), 100)
    sql = f"""
        SELECT contract_id, tender_title, buyer_name,
               price_excl_vat, price_incl_vat, announcement_date, contract_status
        FROM {SNOWFLAKE_TABLE}
        WHERE (:buyer_name IS NULL OR buyer_name ILIKE '%' || :buyer_name || '%')
        ORDER BY announcement_date DESC NULLS LAST
        LIMIT :limit
    """
    return run_query(sql, {"buyer_name": buyer_name, "limit": limit})


@mcp.tool()
def get_top_buyers(n: int = 10) -> list[dict]:
  
    n = min(max(n, 1), 50)
    sql = f
     
    return run_query(sql, {"n": n})


@mcp.tool()
def get_dataset_summary() -> dict:
    
    sql = f
    rows = run_query(sql)
    return rows[0]


if __name__ == "__main__":
    mcp.run()