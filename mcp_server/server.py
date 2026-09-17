
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
import shared_tools

mcp = FastMCP("Procurement Data Server")

mcp.tool()(shared_tools.search_contracts)
mcp.tool()(shared_tools.get_top_buyers)
mcp.tool()(shared_tools.get_dataset_summary)

if __name__ == "__main__":
    mcp.run()