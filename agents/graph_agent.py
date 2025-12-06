# agents/graph_agent.py

from agents.simple_agent import SimpleAgent
from config import GROQ_MODEL


# Graph agent with simple instructions
graph_agent = SimpleAgent(
    model=GROQ_MODEL,
    system="""
You are an expert knowledge graph extractor.

Your tasks:
- Analyze the input text.
- Identify the MAJOR concepts.
- Identify relationships between concepts.
- Return ONLY structured bullet points.
- Do NOT invent extra information.
- Base everything strictly on the text.
"""
)


def build_graph(text: str):
    response = graph_agent.run([
        {
            "role": "user",
            "content": (
                f"Extract the key relationships from this text:\n\n{text}\n\n"
                "Return the answer as bullet points describing relationships."
            )
        }
    ])
    
    return response
