# api/app.py
from fastapi import FastAPI
from pydantic import BaseModel

from agents.web_agent import web_agent
from agents.ingestion_agent import ingest_items
from agents.rag_agent import answer_with_rag
from agents.graph_agent import describe_relationships
from agents.validator_agent import validate_sources
from agents.report_agent import generate_report
from agents.manager_agent import manager_agent


class Query(BaseModel):
    question: str


app = FastAPI(title="Agentic RAG Research API (Gemini Powered)")


@app.post("/query")
def run_query(payload: Query):
    q = payload.question

    web_res = web_agent.run(q).content
    rag_res = answer_with_rag(q)
    graph_res = describe_relationships(q)
    validated = validate_sources({
        "rag": rag_res,
        "graph": graph_res,
        "web": web_res
    })
    report = generate_report(validated)

    return {
        "web_results": web_res,
        "rag_results": rag_res,
        "graph_results": graph_res,
        "validated": validated,
        "final_report": report,
    }
