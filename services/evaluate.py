# services/evaluate.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


"""
Evaluation script for the Agentic Research Assistant.

Metrics:
- Download / ingestion success rate
- RAG retrieval coverage
- Groundedness score (how much of the final report is supported by ingested docs)
- Hallucination rate
- Report completeness (sections present)

Run from project root as:
  python -m services.evaluate "your research question"
or:
  python services/evaluate.py
"""

import sys
import math
from typing import List, Dict

from sentence_transformers import SentenceTransformer

from config import TOP_K
from agents.web_agent import web_search
from agents.ingestion_agent import ingest_items
from agents.rag_agent import run_rag
from agents.graph_agent import build_graph
from agents.validator_agent import validate
from agents.report_agent import generate_report
from services.vector_store import search_similar


# -----------------------------
# Lazy embedding model for eval
# -----------------------------
_eval_embedder = None


def get_eval_embedder():
    global _eval_embedder
    if _eval_embedder is None:
        print("[*] Loading evaluation embedding model...")
        _eval_embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _eval_embedder


# -----------------------------
# Utility: sentence splitting
# -----------------------------
def split_into_sentences(text: str) -> List[str]:
    # Very simple splitter (you can improve later)
    import re
    raw = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    sentences = [s.strip() for s in raw if len(s.strip()) > 0]
    return sentences


# -----------------------------
# Metric 1: Groundedness score
# -----------------------------
def compute_groundedness(final_report: str, distance_threshold: float = 0.35) -> Dict[str, float]:
    """
    For each sentence in the final report:
      - embed sentence
      - search top-1 similar chunk from vector DB
      - if distance <= threshold => grounded
    """
    sentences = split_into_sentences(final_report)
    # Ignore very short sentences
    sentences = [s for s in sentences if len(s.split()) >= 6]

    if not sentences:
        return {"grounded_score": 0.0, "hallucination_rate": 1.0, "total_sentences": 0}

    embedder = get_eval_embedder()

    grounded = 0
    distances = []

    for s in sentences:
        vec = embedder.encode(s).tolist()
        docs = search_similar(vec, top_k=1)
        if not docs:
            # No match at all -> treat as hallucinated
            distances.append(float("inf"))
            continue
        d = docs[0].get("distance", None)
        if d is None:
            continue
        distances.append(d)
        if d <= distance_threshold:
            grounded += 1

    total = len(sentences)
    grounded_score = grounded / total if total > 0 else 0.0
    hallucination_rate = 1.0 - grounded_score

    return {
        "grounded_score": grounded_score,
        "hallucination_rate": hallucination_rate,
        "total_sentences": total,
        "avg_distance": sum(distances) / len(distances) if distances else math.inf,
    }


# -----------------------------
# Metric 2: Report completeness
# -----------------------------
def compute_report_completeness(final_report: str) -> Dict[str, float]:
    required_sections = [
        "Executive Summary",
        "Key Findings",
        "Detailed Analysis",
        "Limitations",
        "Sources",
    ]

    present = 0
    lower = final_report.lower()
    for sec in required_sections:
        if sec.lower() in lower:
            present += 1

    completeness = present / len(required_sections)

    return {
        "sections_present": present,
        "sections_total": len(required_sections),
        "completeness_score": completeness,
    }


# -----------------------------
# Metric 3: Ingestion success
# -----------------------------
def compute_ingestion_metrics(ingest_result: List[Dict]) -> Dict[str, float]:
    """
    ingest_result = [
      {"url": "...", "chunks_stored": int, ...},
      ...
    ]
    """
    if not ingest_result:
        return {
            "num_urls": 0,
            "num_success": 0,
            "total_chunks": 0,
            "ingestion_success_rate": 0.0,
        }

    num_urls = len(ingest_result)
    num_success = sum(1 for r in ingest_result if r.get("chunks_stored", 0) > 0)
    total_chunks = sum(r.get("chunks_stored", 0) for r in ingest_result)

    return {
        "num_urls": num_urls,
        "num_success": num_success,
        "total_chunks": total_chunks,
        "ingestion_success_rate": num_success / num_urls if num_urls > 0 else 0.0,
    }


# -----------------------------
# Metric 4: RAG retrieval coverage
# -----------------------------
def compute_rag_retrieval_coverage(question: str, top_k: int = TOP_K) -> Dict[str, float]:
    """
    We re-embed the question and check how many chunks we get back.
    This isn't true recall (no labels), but a quick check:
    - did the question find any neighbors at all?
    """
    embedder = get_eval_embedder()
    q_vec = embedder.encode(question).tolist()
    docs = search_similar(q_vec, top_k=top_k)
    num_docs = len(docs)

    return {
        "retrieved_chunks": num_docs,
        "retrieval_has_context": 1.0 if num_docs > 0 else 0.0,
    }


# -----------------------------
# Run full pipeline + evaluate
# -----------------------------
def run_and_evaluate(question: str):
    print("===== EVALUATION RUN STARTED =====")
    print(f"Question: {question}\n")

    # --- 1. Web search ---
    print("[1] Running web search...")
    links = web_search(question)
    print(f"    -> Got {len(links)} links")

    # --- 2. Ingestion ---
    # --- 2. Ingestion (SKIPPED for faster eval) ---    
    print("[2] Skipping ingestion – using existing vector DB for evaluation.")
    ingest_result = []
    ingest_metrics = compute_ingestion_metrics(ingest_result)

    # --- 3. RAG answer ---
    print("[3] Running RAG agent...")
    rag_answer = run_rag(question)

    # --- 4. Graph agent ---
    print("[4] Running graph agent...")
    graph_view = build_graph(rag_answer)

    # --- 5. Validation ---
    print("[5] Running validator agent...")
    combined_text = f"""
Web Links:
{links}

RAG Answer:
{rag_answer}

Graph View:
{graph_view}
"""
    validated = validate(combined_text)

    # --- 6. Final report ---
    print("[6] Generating final report...")
    final_report = generate_report(question, validated)

    # --- 7. RAG retrieval coverage ---
    rag_metrics = compute_rag_retrieval_coverage(question, top_k=TOP_K)

    # --- 8. Groundedness & hallucination ---
    print("[7] Computing groundedness & hallucination metrics...")
    grounding = compute_groundedness(final_report)

    # --- 9. Report completeness ---
    print("[8] Checking report completeness...")
    completeness = compute_report_completeness(final_report)

    # --- Aggregate scoring (simple heuristic) ---
    # You can tune weights later
    overall_score = (
        0.3 * grounding["grounded_score"]
        + 0.2 * (1.0 - grounding["hallucination_rate"])
        + 0.2 * ingest_metrics["ingestion_success_rate"]
        + 0.2 * completeness["completeness_score"]
        + 0.1 * rag_metrics["retrieval_has_context"]
    )

    print("\n\n===== EVALUATION SUMMARY =====")
    print(f"Ingestion:")
    print(f"  - URLs processed:          {ingest_metrics['num_urls']}")
    print(f"  - URLs with chunks stored: {ingest_metrics['num_success']}")
    print(f"  - Total chunks stored:     {ingest_metrics['total_chunks']}")
    print(f"  - Ingestion success rate:  {ingest_metrics['ingestion_success_rate']:.2f}")

    print("\nRAG Retrieval:")
    print(f"  - Retrieved chunks (top_k={TOP_K}): {rag_metrics['retrieved_chunks']}")
    print(f"  - Retrieval has context?:          {bool(rag_metrics['retrieval_has_context'])}")

    print("\nGroundedness:")
    print(f"  - Sentences evaluated:  {grounding['total_sentences']}")
    print(f"  - Grounded score:       {grounding['grounded_score']:.2f}")
    print(f"  - Hallucination rate:   {grounding['hallucination_rate']:.2f}")
    print(f"  - Avg distance (lower better): {grounding['avg_distance']:.4f}")

    print("\nReport Completeness:")
    print(f"  - Sections present:     {completeness['sections_present']}/{completeness['sections_total']}")
    print(f"  - Completeness score:   {completeness['completeness_score']:.2f}")

    print("\nOverall Project Score (0–1): {:.2f}".format(overall_score))

    print("\n===== FINAL REPORT (for reference) =====\n")
    print(final_report)

    return {
        "ingestion": ingest_metrics,
        "rag": rag_metrics,
        "grounding": grounding,
        "completeness": completeness,
        "overall_score": overall_score,
        "final_report": final_report,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Enter a research question to evaluate: ").strip()

    run_and_evaluate(question)
