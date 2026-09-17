"""
Central config loader. Reads Snowflake connection details from .env.
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "ETL_PROJECT")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
SNOWFLAKE_TABLE = os.getenv("SNOWFLAKE_TABLE", "TRANSACTIONS")


def get_db_url() -> str:
    """Builds the SQLAlchemy connection string for Snowflake.
    User/password are URL-encoded so special characters (e.g. @) in the
    password don't break the URL structure."""
    user = quote_plus(SNOWFLAKE_USER)
    password = quote_plus(SNOWFLAKE_PASSWORD)
    return (
        f"snowflake://{user}:{password}"
        f"@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}"
        f"?warehouse={SNOWFLAKE_WAREHOUSE}"
    )
