# agents/report_agent.py

from agents.simple_agent import SimpleAgent
from config import GROQ_MODEL


# Report Agent
report_agent = SimpleAgent(
    model=GROQ_MODEL,
    system="""
You are a senior research assistant.
Write polished, well-structured, professional research reports.
Follow the exact sections requested.
"""
)


def generate_report(question: str, validated_summary: str):

    response = report_agent.run([
        {
            "role": "user",
            "content": f"""
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
"""
        }
    ])

    return response
