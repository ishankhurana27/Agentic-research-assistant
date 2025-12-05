# services/embedding_service.py

from sentence_transformers import SentenceTransformer

# IMPORTANT:
# Your original project was using MiniLM embeddings (because pgvector dim = 384)
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str):
    """
    Return a Python list embedding for text.
    Your original code expects a list, not numpy array.
    """
    emb = model.encode(text)
    return emb.tolist()
