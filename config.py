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
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_FAST_MODEL = "llama-3.1-8b-instant"  


SERPER_API_KEY="c3eae267e33b66c0194668e295b98cb240859505"
SOURCE_NAME = "web"





