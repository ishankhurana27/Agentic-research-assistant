# agents/validator_agent.py

from agno.agent import Agent
from agno.models.groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY

# Create agent using Agno v2 model object
validator_agent = Agent(
    id="validator-agent",
    name="Validator Agent",
    model=Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY)
)

def validate(view: dict):
    """
    Validate claims using deductive reasoning.
    No new facts should be invented.
    """
    result = validator_agent.run(
        system="""
<role>
You are a logic-based validator.
</role>

<instructions>
- Validate claims ONLY using reasoning.
- Do NOT add new facts.
- Identify inconsistencies.
- If something cannot be validated, say so.
</instructions>
""",
        messages=[
            {
                "role": "user",
                "content": f"Validate this content logically:\n\n{view}"
            }
        ]
    )

    return result.content
