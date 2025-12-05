from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.function import FunctionTool

from agents.web_agent import web_agent
from agents.ingestion_agent import ingest_items
from agents.rag_agent import answer_with_rag
from agents.graph_agent import describe_relationships
from agents.validator_agent import validate_sources
from agents.report_agent import generate_report

from config import GROQ_MODEL, GROQ_API_KEY

manager_agent = Agent(
    name="Manager",
    role="Master coordinator",
    model=Groq(id=GROQ_MODEL, api_key=GROQ_API_KEY),
    instructions=[
        "Plan step-by-step.",
        "Use tools: web_search, ingest_items, rag_query, graph_query, validate_sources, generate_report",
        "Final output must ALWAYS call generate_report."
    ],
    tools=[
        FunctionTool(web_agent.run, name="web_search"),
        FunctionTool(ingest_items, name="ingest_items"),
        FunctionTool(answer_with_rag, name="rag_query"),
        FunctionTool(describe_relationships, name="graph_query"),
        FunctionTool(validate_sources, name="validate_sources"),
        FunctionTool(generate_report, name="generate_report"),
    ],
)
