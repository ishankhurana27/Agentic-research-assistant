# services/web_search.py
import requests

def web_search_service(query: str, top_k: int = 5):
    """
    Performs a free web search using DuckDuckGo Instant API.
    Returns a list of dicts:
    [
        {
            "url": "...",
            "title": "...",
            "is_pdf": bool
        }
    ]
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "no_redirect": 1,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        results = []

        # Extract "RelatedTopics" URLs
        for topic in data.get("RelatedTopics", []):
            if "FirstURL" in topic:
                link = topic["FirstURL"]
                results.append({
                    "url": link,
                    "title": topic.get("Text", "Webpage"),
                    "is_pdf": link.lower().endswith(".pdf")
                })

        # Fallback to AbstractURL
        if "AbstractURL" in data and data["AbstractURL"]:
            link = data["AbstractURL"]
            results.append({
                "url": link,
                "title": data.get("Heading", "Webpage"),
                "is_pdf": link.lower().endswith(".pdf")
            })

        return results[:top_k]

    except Exception as e:
        print(f"❌ Web search error: {e}")
        return []
