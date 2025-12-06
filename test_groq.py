from groq import Groq
import os

print("GROQ_API_KEY =", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    models = client.models.list()
    print(models)
except Exception as e:
    print("ERROR:", e)
