# Procurement AI Agent

This project lets an AI agent answer questions about Slovak public procurement data using plain English instead of SQL. It's built on top of the data pipeline in [eks-procurement-etl-pipeline](https://github.com/15vishal-p/eks-procurement-etl-pipeline), which cleans and loads the raw data into Snowflake. This repo picks up from there - it's about exposing that data through an API, an MCP server, and an agent, not about the data pipeline itself.

## What's in here

- A FastAPI service with a few read-only endpoints over the procurement data
- An MCP server that exposes those same queries as tools an AI agent can call
- A LangChain/LangGraph agent that picks the right tool based on what you ask it
- A small RAG layer for semantic search - finding tenders by what they mean, not just exact keywords (e.g. "office supplies" matching the Slovak "Kancelárske potreby")
- Docker + a GitHub Actions pipeline that lints and tests the code on every push

## API endpoints

- `GET /contracts` - list or search contracts, paginated, can filter by buyer
- `GET /contracts/{id}` - one contract by ID
- `GET /buyers/top` - top buyers by total spend
- `GET /stats/summary` - overall dataset stats

## Agent tools

The MCP server and the agent both use the same four functions, defined once in `shared_tools.py`:

- `search_contracts`
- `get_top_buyers`
- `get_dataset_summary`
- `semantic_search_tenders` (the RAG one)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Snowflake and Gemini API credentials.

## Running things

**API:**
```
uvicorn app.main:app --reload
```
Docs at http://127.0.0.1:8000/docs

**MCP server:**
```
python mcp_server/server.py
```

**Build the semantic search index** (do this once before using the semantic search tool):
```
python vector_store/build_index.py
```

**Agent (chat in your terminal):**
```
python agent/main.py
```

## Docker

```
docker build -t procurement-api .
docker run -p 8000:8000 --env-file .env procurement-api
```

## CI

Every push to `main` runs flake8 and pytest automatically - see `.github/workflows/ci.yml`.

## Structure

```
app/
  main.py          - FastAPI app
  config.py        - Snowflake config from .env
  db.py            - SQLAlchemy connection + query helper
  models.py        - Pydantic response models
  routers/         - contracts, buyers, stats endpoints

shared_tools.py    - the actual query functions, used by both the MCP server and the agent

mcp_server/
  server.py        - wraps shared_tools.py as MCP tools

agent/
  main.py          - the LangChain/LangGraph agent

vector_store/
  build_index.py   - builds the Chroma vector store for semantic search

tests/             - basic smoke tests, don't need Snowflake credentials to run
Dockerfile
.github/workflows/ - CI pipeline
```

## A few notes on decisions made along the way

- The MCP server and the agent both wrap the same functions in `shared_tools.py` instead of duplicating the query logic in two places.
- The agent doesn't actually connect to the MCP server over the MCP protocol - `langchain-mcp-adapters` had a dependency conflict with FastMCP's bundled `mcp` package when I tried it, so the agent just imports the shared functions directly as LangChain tools instead. The MCP server itself still works fine on its own for any MCP-compatible client.
- The semantic search index only covers 100 tender titles, not the full ~514k rows. Embedding all of them would take a while and run into free-tier API rate limits, so this is a representative sample for demo purposes. A real version would use a proper batch embedding pipeline over the whole dataset.
- The API only reads data, so it doesn't run into the bind-parameter limits that came up on the loading side in the ETL repo - that's a write-side problem specific to inserting large batches into a wide table.