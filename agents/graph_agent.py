# agents/graph_agent.py

from agno.agent import Agent
from agno.models.groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY

graph_agent = Agent(
    id="graph-agent",
    name="Graph Agent",
    model=Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY),
    instructions=[
        "Analyze the text and describe relationships between the major concepts.",
        "Return only structured bullet points.",
    ]
)

def build_graph(text: str):
    result = graph_agent.run(
        messages=[
            {"role": "user", "content": f"Extract key relationships:\n\n{text}"}
        ]
    )
    return result.content
