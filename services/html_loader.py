import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# -------------------------
# Directory Setup
# -------------------------
BASE_DIR = Path("data")
RAW_HTML_DIR = BASE_DIR / "raw_html"
RAW_HTML_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# 1. Download HTML File
# -------------------------
def download_html(url: str) -> str:
    """
    Downloads HTML page and stores a local copy.
    Returns the path to the saved HTML file.
    """
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        filename = url.replace("https://", "").replace("http://", "").replace("/", "_")
        filepath = RAW_HTML_DIR / f"{filename}.html"

        with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(r.text)

        return str(filepath)

    except Exception as e:
        print(f"❌ Error downloading HTML: {e}")
        return None


# -------------------------
# 2. Extract & Clean HTML
# -------------------------
def extract_text_from_html(filepath: str) -> str:
    """
    Given an HTML file path, extracts readable text.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts & styles
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        text = soup.get_text(separator="\n")
        cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        return cleaned

    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return ""


# -------------------------
# 3. Full Pipeline: Fetch + Clean
# -------------------------
def fetch_and_clean_html(url: str):
    """
    Downloads HTML → stores locally → extracts & cleans text.
    Returns (title, text)
    """
    filepath = download_html(url)
    if not filepath:
        return ("Untitled", "")

    text = extract_text_from_html(filepath)

    # Best-effort title extraction
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        title = soup.title.string.strip() if soup.title else url
    except:
        title = url

    return (title, text)
