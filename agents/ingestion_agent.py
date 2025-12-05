# agents/ingestion_agent.py
from services.html_loader import fetch_and_clean_html
from services.pdf_loader import extract_text_from_pdf
from services.vector_store import store_document

def ingest_items(items):
    results = []

    for item in items:
        url = item["url"]
        is_pdf = item["is_pdf"]

        try:
            if is_pdf:
                text = extract_text_from_pdf(url)
                title = url.split("/")[-1]
            else:
                title, text = fetch_and_clean_html(url)

            chunks = store_document(title, text)
            results.append({"url": url, "chunks_stored": len(chunks)})

        except Exception as e:
            print(f"[!] Error ingesting {url}: {e}")
            results.append({"url": url, "chunks_stored": 0})

    return results
