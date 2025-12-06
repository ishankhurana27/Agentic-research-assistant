# agents/rag_agent.py

from agents.simple_agent import SimpleAgent
from config import GROQ_MODEL, TOP_K
from services.vector_store import search_similar
from sentence_transformers import SentenceTransformer

embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        print("[*] Loading embedding model...")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder

# Create the agent (no Agno!)
rag_agent = SimpleAgent(
    model=GROQ_MODEL,
    system="You are a Retrieval-Augmented Generation agent. Use ONLY the provided context."
)

def run_rag(question: str):
    emb = get_embedder().encode(question).tolist()

    docs = search_similar(emb, top_k=TOP_K)

    if not docs:
        context = "No relevant documents found."
    else:
        context = "\n\n".join(
            f"[{d['source']}] {d['title']}\n{d['content'][:800]}"
            for d in docs
        )

    response = rag_agent.run([
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                "Answer strictly using the above context."
            )
        }
    ])
    
    return response
