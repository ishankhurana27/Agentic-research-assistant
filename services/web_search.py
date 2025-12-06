# services/web_search.py

import requests

def web_search_service(query: str, top_k: int = 5):
    """
    Performs a free web search using DuckDuckGo Instant API.
    Returns a simple list of URLs.
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

        urls = []

        # Extract URLs from "RelatedTopics"
        for topic in data.get("RelatedTopics", []):
            if "FirstURL" in topic:
                urls.append(topic["FirstURL"])

        # Fallback to AbstractURL
        if data.get("AbstractURL"):
            urls.append(data["AbstractURL"])

        # Return only top-k unique URLs
        clean_urls = []
        for u in urls:
            if u not in clean_urls:
                clean_urls.append(u)

        return clean_urls[:top_k]

    except Exception as e:
        print(f"❌ Web search error: {e}")
        return []
