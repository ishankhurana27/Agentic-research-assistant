# agents/manager_agent.py

from agents.simple_agent import SimpleAgent
from agents.web_agent import web_search
from agents.ingestion_agent import ingest_items
from agents.rag_agent import run_rag
from agents.graph_agent import build_graph
from agents.validator_agent import validate
from agents.report_agent import generate_report


manager_agent = SimpleAgent(
    model="llama-3.3-70b-versatile",
    system="""
You are the MASTER MANAGER AGENT.

Your job:
1. Plan the research workflow.
2. Use the provided helper functions (not tools).
3. Never hallucinate steps.
4. Always follow this pipeline:

Pipeline:
1. Clean search query
2. Search web
3. Ingest pages & PDFs
4. Run RAG answer
5. Build graph of relations
6. Validate the summary logically
7. Produce final research report

You must ALWAYS return a final report.
"""
)


def run_manager_pipeline(question: str):
    """
    Full agentic research pipeline orchestrated manually.
    """

    # 1. Refine + Search
    print("\n[*] Step 1: Searching web ...")
    urls = web_search(question)

    # 2. Ingestion
    print("\n[*] Step 2: Ingesting documents ...")
    ingestion_results = ingest_items(urls)

    # 3. RAG
    print("\n[*] Step 3: Running RAG ...")
    rag_answer = run_rag(question)

    # 4. Graph
    print("\n[*] Step 4: Building knowledge graph ...")
    graph = build_graph(rag_answer)

    # 5. Validation
    print("\n[*] Step 5: Validating RAG answer ...")
    validated = validate(rag_answer)

    # 6. Report
    print("\n[*] Step 6: Generating final report ...")
    final_report = generate_report(question, validated)

    return {
        "question": question,
        "rag_answer": rag_answer,
        "graph": graph,
        "validated_summary": validated,
        "report": final_report
    }
