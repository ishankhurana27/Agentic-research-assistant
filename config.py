import os
from dotenv import load_dotenv

load_dotenv()

# ---- LOCAL EMBEDDING DIMENSION ----
# all-MiniLM-L6-v2 output dimension
EMBEDDING_DIM = 384

# ---- DATABASE ----
DB_URL = os.getenv("DB_URL")

# ---- RAG ----
TOP_K = 5

# ---- GROQ LLM ----
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Good default general model
GROQ_MODEL = "meta-llama:llama-3.3-70b-versatile"







