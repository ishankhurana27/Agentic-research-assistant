# main.py

from agents.web_agent import web_search
from agents.ingestion_agent import ingest_items
from agents.rag_agent import run_rag
from agents.graph_agent import build_graph
from agents.validator_agent import validate
from agents.report_agent import generate_report

def build_ingestion_items(links):
    items = []
    for url in links:
        items.append({
            "url": url,
            "is_pdf": str(url).lower().endswith(".pdf")
        })
    return items

def run_research_pipeline(question):
    print("[*] Searching web for candidate documents...")
    links = web_search(question)

    print(f"[*] Found {len(links)} links. Ingesting into vector DB...")
    items = build_ingestion_items(links)
    ingest_result = ingest_items(items)
    print(f"[*] Ingestion done. Stored {sum(r['chunks_stored'] for r in ingest_result)} chunks.")

    print("[*] Running RAG agent...")
    rag_view = run_rag(question)

    print("[*] Running graph agent...")
    graph_view = build_graph(rag_view)

    combined = {"web": links, "rag": rag_view, "graph": graph_view}

    print("[*] Validating summary...")
    validated = validate(combined)

    print("[*] Generating final report...")
    final_report = generate_report(question, validated)

    return final_report

if __name__ == "__main__":
    print("MAIN IMPORTED")
    print("MAIN STARTED")
    q = input("Enter your research question: ")
    report = run_research_pipeline(q)
    print("\n===== FINAL REPORT =====\n")
    print(report)
