# agents/rag_agent.py

from agno.agent import Agent
from config import GROQ_MODEL
from services.embedding_service import embed_text
from services.vector_store import search_similar

# Create agent
rag_agent = Agent(
    id="rag-agent",
    name="RAG Agent",
    model=GROQ_MODEL
)

def run_rag(question: str, top_k: int = 5):
    # 1. Embed the question
    query_vec = embed_text(question)

    # 2. Fetch similar documents
    docs = search_similar(query_vec, top_k)

    # Build context string
    context = ""
    for d in docs:
        context += f"[{d['url']}] {d['title']}\n{d['content']}\n\n"

    # 3. Ask LLM using Agno v2 run() syntax
    result = rag_agent.run(
        input=(
            "Use ONLY the context below to answer the question.\n"
            "If the context is irrelevant or empty, say so.\n\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}"
        ),
        system="Retrieve and answer strictly using context. No outside facts."
    )

    return result.content
