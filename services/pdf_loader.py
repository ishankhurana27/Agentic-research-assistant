import requests
from pathlib import Path
import fitz  # PyMuPDF

BASE_DIR = Path("data")
RAW_PDF_DIR = BASE_DIR / "raw_pdf"
RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# Download PDF file
# -------------------------
def download_pdf(url: str) -> str:
    """
    Downloads a PDF from URL and saves locally.
    Returns local PDF path.
    """
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()

        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        filepath = RAW_PDF_DIR / filename

        with open(filepath, "wb") as f:
            f.write(r.content)

        return str(filepath)

    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
        return None


# -------------------------
# Extract text from PDF
# -------------------------
def extract_text_from_pdf(url_or_path: str):
    """
    If input is URL → download PDF.
    If input is local path → open directly.
    Returns extracted text.
    """
    # Detect URL
    if url_or_path.startswith("http"):
        local_path = download_pdf(url_or_path)
        if not local_path:
            return ""
    else:
        local_path = url_or_path

    try:
        doc = fitz.open(local_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        return full_text

    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return ""
