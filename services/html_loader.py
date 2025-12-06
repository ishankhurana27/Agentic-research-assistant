# services/html_loader.py

import os
import requests
import re
from pathlib import Path
from bs4 import BeautifulSoup

# -------------------------
# Directory Setup
# -------------------------
BASE_DIR = Path("data")
RAW_HTML_DIR = BASE_DIR / "raw_html"
RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# 1. Download HTML (URL → local file)
# -------------------------
def download_html(url: str) -> str:
    """
    Downloads an HTML page and saves it locally.
    Returns the filepath if successful, else None.
    """

    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()

        # Sanitize filename (remove ?, =, :, /, \ etc.)
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", url)

        filepath = RAW_HTML_DIR / f"{safe}.html"

        with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(r.text)

        return str(filepath)

    except Exception as e:
        print(f"[!] HTML download failed: {e}")
        return None


# -------------------------
# 2. Extract & Clean HTML (local file → text)
# -------------------------
def fetch_and_clean_html(filepath: str):
    """
    Loads and cleans HTML *from a local file*.
    Returns (title, cleaned_text)
    """

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return ("Untitled", "")

    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    try:
        title = soup.title.string.strip() if soup.title else filepath
    except:
        title = filepath

    # Remove scripts & styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Extract clean text
    text = soup.get_text(separator="\n")
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())

    return (title, cleaned)
