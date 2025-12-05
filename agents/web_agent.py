# agents/web_agent.py

from agno.agent import Agent
from agno.models.groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY
from services.web_search import web_search_service

web_agent = Agent(
    id="web-agent",
    name="Web Agent",
    model=Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY)
)

def web_search(query: str):

    result = web_agent.run(
        input=f"Clean this search query: {query}",
        system="""
<role>
You refine search queries.
</role>

<instructions>
- Return ONLY a short search query.
- DO NOT answer the question.
- DO NOT generate sentences.
- DO NOT say anything else.
- Output ONLY 2–4 keywords.
</instructions>
        """,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    refined = result.content.strip()
    print("[*] Refined Query:", refined)

    return web_search_service(refined)
