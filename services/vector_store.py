from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_URL, EMBEDDING_DIM

engine = create_engine(DB_URL, future=True)

# ------------------------------
# Create table (auto on startup)
# ------------------------------
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    source TEXT,
    url TEXT,
    title TEXT,
    content TEXT,
    embedding VECTOR({EMBEDDING_DIM})
);
"""

# Safe: table creation should not freeze (it's fast)
with engine.connect() as conn:
    conn.execute(text(CREATE_TABLE_SQL))
    conn.commit()


# ------------------------------
# Store a document + embedding
# ------------------------------
def store_document(source: str, url: str, title: str, content: str, embedding: list):
    if embedding is None:
        raise ValueError("Embedding missing in store_document()")

    INSERT_SQL = """
        INSERT INTO documents (source, url, title, content, embedding)
        VALUES (:source, :url, :title, :content, :embedding)
    """

    try:
        with engine.connect() as conn:
            conn.execute(
                text(INSERT_SQL),
                {
                    "source": source,
                    "url": url,
                    "title": title,
                    "content": content,
                    "embedding": embedding,
                }
            )
            conn.commit()
    except SQLAlchemyError as e:
        print("❌ Error storing document:", e)
        raise


# ------------------------------
# Semantic similarity search
# ------------------------------
def search_similar(query_vec: list, top_k: int):
    # Convert Python list → pgvector format
    pg_vec = "[" + ",".join(str(x) for x in query_vec) + "]"

    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT id, source, url, title, content,
                       embedding <-> (:query_vec)::vector AS distance
                FROM documents
                ORDER BY embedding <-> (:query_vec)::vector
                LIMIT :top_k;
            """),
            {"query_vec": pg_vec, "top_k": top_k}
        )

        return [dict(r._mapping) for r in rows]
