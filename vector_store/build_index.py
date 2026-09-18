"""
Builds a local vector store (Chroma) of tender titles for semantic search.

Scoped to a sample of distinct tender titles (see SAMPLE_SIZE below) rather
than the full 514k rows - this keeps embedding generation within free-tier
API rate limits for a demo build. Embeds in small batches with pauses
between them to stay under the free tier's requests-per-minute limit.
A production version would embed the full corpus using a batch embedding
pipeline with proper queuing rather than a one-off script.

Run with: python vector_store/build_index.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db import run_query  # noqa: E402
from app.config import SNOWFLAKE_TABLE  # noqa: E402
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # noqa: E402
import chromadb  # noqa: E402

SAMPLE_SIZE = 100
CHUNK_SIZE = 10
DELAY_BETWEEN_CHUNKS = 8  # seconds
COLLECTION_NAME = "tender_titles"
PERSIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")


def embed_with_retry(embeddings_client, texts):
    """Embeds texts in small chunks, pausing between them, retrying on rate limits."""
    all_vectors = []
    for i in range(0, len(texts), CHUNK_SIZE):
        chunk = texts[i:i + CHUNK_SIZE]
        while True:
            try:
                vectors = embeddings_client.embed_documents(chunk)
                all_vectors.extend(vectors)
                break
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    print("  Rate limited, waiting 35s before retry...")
                    time.sleep(35)
                else:
                    raise
        print(f"  Embedded {min(i + CHUNK_SIZE, len(texts))}/{len(texts)}")
        time.sleep(DELAY_BETWEEN_CHUNKS)
    return all_vectors


def main():
    print(f"Fetching up to {SAMPLE_SIZE} distinct tender titles from Snowflake...")
    sql = f"""
        SELECT DISTINCT contract_id, tender_title
        FROM {SNOWFLAKE_TABLE}
        WHERE tender_title IS NOT NULL
        LIMIT {SAMPLE_SIZE}
    """
    rows = run_query(sql)
    print(f"Fetched {len(rows)} rows")

    texts = [row["tender_title"] for row in rows]
    ids = [f"{i}_{row['contract_id']}" for i, row in enumerate(rows)]
    metadatas = [{"contract_id": row["contract_id"]} for row in rows]

    print("Generating embeddings (in small batches, this will take a few minutes)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectors = embed_with_retry(embeddings, texts)

    print("Saving to vector store...")
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=vectors)

    print(f"Vector store built and saved to {PERSIST_DIR}")
    print(f"Indexed {len(texts)} tender titles")


if __name__ == "__main__":
    main()