"""
LangChain/LangGraph agent that answers natural-language questions about
the procurement data.

Note: this wraps the same functions in shared_tools.py directly as
LangChain tools, rather than connecting through the MCP server via
langchain-mcp-adapters. That adapter currently has a dependency
conflict with fastmcp's bundled mcp package (version mismatch on
mcp.shared.context.RequestContext) - rather than chase that conflict,
the agent and the MCP server both wrap the same underlying functions
from shared_tools.py, so there's one source of truth for the actual
data-access logic either way.

Run with: python agent/main.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

import shared_tools

load_dotenv()

search_contracts = tool(shared_tools.search_contracts)
get_top_buyers = tool(shared_tools.get_top_buyers)
get_dataset_summary = tool(shared_tools.get_dataset_summary)

tools = [search_contracts, get_top_buyers, get_dataset_summary]


def main():
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    agent = create_react_agent(llm, tools)

    print("\nProcurement Data Agent ready. Ask a question (or 'quit' to exit).\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue

        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        answer = result["messages"][-1].content
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()