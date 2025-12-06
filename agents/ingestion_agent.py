# agents/ingestion_agent.py

from services.html_loader import download_html, fetch_and_clean_html
from services.pdf_loader import extract_text_from_pdf
from services.vector_store import store_document


def ingest_items(items):
    results = []

    for item in items:
        url = item["url"]
        is_pdf = item["is_pdf"]

        try:
            # 1. Download content
            if is_pdf:
                print(f"[*] Downloading PDF: {url}")
                filepath = extract_text_from_pdf(url)
                title = url.split("/")[-1]
                text = filepath  # function returns extracted text
            else:
                print(f"[*] Downloading HTML: {url}")
                filepath = download_html(url)

                if not filepath:
                    raise Exception("File download failed")

                title, text = fetch_and_clean_html(filepath)

            # 2. Store in vector DB (chunks + embeddings)
            chunks = store_document(url=url, title=title, content=text)

            results.append({
                "url": url,
                "chunks_stored": len(chunks)
            })

        except Exception as e:
            print(f"[!] Error ingesting {url}: {e}")
            results.append({"url": url, "chunks_stored": 0})

    return results
