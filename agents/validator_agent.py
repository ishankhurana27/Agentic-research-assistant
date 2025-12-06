# agents/validator_agent.py

from agents.simple_agent import SimpleAgent
from config import GROQ_MODEL


# Use same model as RAG or switch to a fast model if you want.
validator_agent = SimpleAgent(
    model=GROQ_MODEL,
    system="""
You are a logic-based validator.

Your task:
- Validate claims ONLY using logical reasoning.
- Do NOT invent new facts.
- Identify inconsistencies clearly.
- If a claim cannot be validated, say so explicitly.
"""
)


def validate(view: dict):
    """
    Validate structured content logically.
    """

    response = validator_agent.run([
        {
            "role": "user",
            "content": f"Validate this content logically:\n\n{view}"
        }
    ])

    return response
