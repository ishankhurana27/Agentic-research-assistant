# agents/report_agent.py
from agno.agent import Agent
from agno.models.groq import Groq
from config import GROQ_MODEL, GROQ_API_KEY

report_agent = Agent(
    id="report-agent",
    name="Report Agent",
    model=Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY)
)

def generate_report(question: str, validated_summary: str):
    result = report_agent.run(
        system="Write a polished, structured final research report.",
        messages=[
            {"role": "user", "content":
f"""
Write a structured research report.

Question: {question}

Validated Summary:
{validated_summary}

Sections:
- Executive Summary
- Key Findings
- Detailed Analysis
- Limitations
- Sources
"""}
        ]
    )
    return result.content
