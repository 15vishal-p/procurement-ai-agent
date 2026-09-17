"""
Shared query functions for the procurement dataset.

Both the MCP server (mcp_server/server.py) and the LangChain agent
(agent/main.py) wrap these same functions as tools - one source of
truth for the actual data-access logic, two different ways of
exposing it (MCP protocol vs. direct LangChain tools).
"""
from app.db import run_query
from app.config import SNOWFLAKE_TABLE


def search_contracts(buyer_name: str = None, limit: int = 20) -> list[dict]:
    """
    Search procurement contracts, optionally filtered by buyer name.

    Args:
        buyer_name: Partial or full buyer name to filter by (optional).
        limit: Maximum number of contracts to return (default 20, max 100).
    """
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


def get_top_buyers(n: int = 10) -> list[dict]:
    """
    Get the top N buyers ranked by total contract value.

    Args:
        n: Number of top buyers to return (default 10, max 50).
    """
    n = min(max(n, 1), 50)
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


def get_dataset_summary() -> dict:
    """
    Get overall summary statistics for the entire procurement dataset:
    total contracts, total value, unique buyers, and date range covered.
    """
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