# services/validation.py

from difflib import SequenceMatcher
from typing import Dict, List


def similarity(a: str, b: str) -> float:
    """
    Simple text similarity using SequenceMatcher.
    Used to detect agreement between sources.
    """
    return SequenceMatcher(None, a, b).ratio()


def detect_conflicts(text_a: str, text_b: str) -> List[str]:
    """
    Finds sentences that contradict each other using naive heuristics:
    - Looks for keywords: not, no, never, impossible
    - Finds mismatched numeric values
    """
    conflicts = []
    a_sentences = text_a.split(".")
    b_sentences = text_b.split(".")

    for a in a_sentences:
        for b in b_sentences:
            if not a.strip() or not b.strip():
                continue

            # Opposing statements heuristic
            if ("not " in a.lower() and " not " not in b.lower()) or \
               (" not " in b.lower() and " not " not in a.lower()):
                if similarity(a, b) > 0.4:
                    conflicts.append(f"Potential contradiction: '{a.strip()}' vs '{b.strip()}'")

            # Numeric mismatch
            import re
            nums_a = re.findall(r"\d+", a)
            nums_b = re.findall(r"\d+", b)

            if nums_a and nums_b:
                # Compare first numbers — naive but effective
                if nums_a[0] != nums_b[0] and similarity(a, b) > 0.3:
                    conflicts.append(
                        f"Numeric inconsistency: '{a.strip()}' vs '{b.strip()}' (numbers differ: {nums_a[0]} vs {nums_b[0]})"
                    )

    return conflicts


def extract_facts(text: str) -> List[str]:
    """
    Splits text into fact-like sentences.
    Could be enhanced using spaCy or NER later.
    """
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 20]
    return sentences[:12]  # limit for readability


def evaluate_reliability(source_name: str) -> float:
    """
    Assign basic reliability scores.
    Extend with custom rules or user preferences.
    """
    source = source_name.lower()

    if "gov" in source or "edu" in source or "official" in source:
        return 0.95
    if "pdf" in source:
        return 0.88
    if "news" in source:
        return 0.75
    if "blog" in source or "medium" in source:
        return 0.55

    return 0.6  # default


def consolidate_sources(sources: Dict[str, str]) -> Dict:
    """
    Consolidate multiple sources:
    - Extract facts
    - Compare similarity
    - Detect conflicts
    - Score reliability
    """

    rag = sources.get("rag_answer", "")
    web = sources.get("web_summary", "")
    graph = sources.get("graph_view", "")

    rag_facts = extract_facts(rag)
    web_facts = extract_facts(web)
    graph_facts = extract_facts(graph)

    # Check conflicts rag <-> web
    conflicts_rw = detect_conflicts(rag, web)
    conflicts_rg = detect_conflicts(rag, graph)
    conflicts_wg = detect_conflicts(web, graph)

    # Reliability scores
    reliability = {
        "rag_answer": evaluate_reliability("pdf"),
        "web_summary": evaluate_reliability("web"),
        "graph_view": evaluate_reliability("graph"),
    }

    return {
        "rag_facts": rag_facts,
        "web_facts": web_facts,
        "graph_facts": graph_facts,
        "conflicts": conflicts_rw + conflicts_rg + conflicts_wg,
        "reliability": reliability,
    }
