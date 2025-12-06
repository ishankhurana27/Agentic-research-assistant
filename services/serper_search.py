# services/serper_search.py

import requests
from config import SERPER_API_KEY

def serper_search(query: str, num_results: int = 10):
    """
    Uses Serper.dev Google Search API and returns:
    [
        {"title": ..., "url": ..., "snippet": ..., "is_pdf": bool}
    ]
    """

    url = "https://google.serper.dev/search"

    payload = {
        "q": query,
        "num": num_results
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
    except Exception as e:
        print("❌ Serper Error:", e)
        return []

    results = []

    for item in data.get("organic", []):
        link = item.get("link", "")
        if not link:
            continue

        results.append({
            "title": item.get("title", ""),
            "url": link,
            "snippet": item.get("snippet", ""),
            "is_pdf": link.lower().endswith(".pdf")
        })

    return results
