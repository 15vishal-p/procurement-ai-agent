# Containerizes the FastAPI service (app/).
# The MCP server and agent are meant to run locally alongside an MCP
# client, so only the API is containerized here.

FROM python:3.12-slim

WORKDIR /code

# Install dependencies first, separately from app code, so Docker can
# cache this layer and skip reinstalling on every code change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual application code
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
