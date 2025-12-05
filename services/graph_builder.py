# services/graph_builder.py

"""
Simple placeholder graph builder so the pipeline works.
You can upgrade later with Neo4j or NetworkX.
"""

def build_graph(context_text: str):
    """
    Creates a simple relationship graph from text.
    Returns a dict describing relationships.
    """
    if not context_text:
        return {"nodes": [], "edges": []}

    # VERY basic splitting logic just to keep project working
    sentences = context_text.split(".")
    nodes = []
    edges = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        nodes.append(sentence[:40])  # node label
        # make a dummy edge to next node
        if len(nodes) > 1:
            edges.append((nodes[-2], nodes[-1]))

    return {
        "nodes": nodes,
        "edges": edges
    }


def explain_graph(graph: dict) -> str:
    """
    Converts the graph into a readable explanation for the agent.
    """
    if not graph or not graph.get("nodes"):
        return "No relationships detected."

    explanation = ["Detected relationships between key statements:\n"]

    for a, b in graph.get("edges", []):
        explanation.append(f"- '{a}' leads to '{b}'")

    return "\n".join(explanation)
