# agents/web_agent.py

from agents.simple_agent import SimpleAgent     # <-- New simple agent
from config import GROQ_FAST_MODEL              # use the fast model for query rewriting
from services.serper_search import serper_search


# Create the agent
web_agent = SimpleAgent(
    model=GROQ_FAST_MODEL,
    system="""
You refine search queries.
Output ONLY 2–4 keywords.
Never answer the question.
Never produce sentences.
"""
)


def web_search(query: str):

    refined = web_agent.run([
        {"role": "user", "content": query}
    ])

    refined = refined.strip()
    print("[*] Refined Query:", refined)

    results = serper_search(refined, num_results=10)

    # return only URLs
    urls = [r["url"] for r in results]
    print(f"[*] Serper returned {len(urls)} links")

    return urls

