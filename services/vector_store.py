# services/vector_store.py

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_URL, EMBEDDING_DIM, SOURCE_NAME
from sentence_transformers import SentenceTransformer

engine = create_engine(DB_URL, future=True)

# Embedding model (lazy load)
embedder = None
def get_embedder():
    global embedder
    if embedder is None:
        print("[*] Loading embedding model...")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder


# -------------------------------
# Create table
# -------------------------------
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

with engine.connect() as conn:
    conn.execute(text(CREATE_TABLE_SQL))
    conn.commit()


# -------------------------------
# Helper: split into chunks
# -------------------------------
def split_into_chunks(text: str, chunk_size=800):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(" ".join(current)) >= chunk_size:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks


# -------------------------------
# Store document: chunks + embeddings
# -------------------------------
def store_document(url: str, title: str, content: str):
    embed = get_embedder()

    chunks = split_into_chunks(content)
    stored = []

    INSERT_SQL = """
        INSERT INTO documents (source, url, title, content, embedding)
        VALUES (:source, :url, :title, :content, :embedding)
    """

    for chunk in chunks:
        try:
            vector = embed.encode(chunk).tolist()

            with engine.connect() as conn:
                conn.execute(
                    text(INSERT_SQL),
                    {
                        "source": "web",
                        "url": url,
                        "title": title,
                        "content": chunk,
                        "embedding": vector,
                    },
                )
                conn.commit()

            stored.append(chunk)

        except SQLAlchemyError as e:
            print("❌ DB error:", e)

    return stored


# -------------------------------
# Search Similar
# -------------------------------
def search_similar(query_vec: list, top_k: int):
    pg_vec = "[" + ",".join(str(x) for x in query_vec) + "]"

    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, source, url, title, content,
                       embedding <-> (:vec)::vector AS distance
                FROM documents
                ORDER BY embedding <-> (:vec)::vector
                LIMIT :k;
                """
            ),
            {"vec": pg_vec, "k": top_k},
        )

        return [dict(r._mapping) for r in rows]
