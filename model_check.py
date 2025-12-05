import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("\nChecking which models support chat/completions...\n")

models = client.models.list().data

chat_models = []

for m in models:
    model_id = m.id
    try:
        # Try a fake completion (won’t charge)
        client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1
        )
        chat_models.append(model_id)
    except Exception:
        pass

print("=== CHAT COMPATIBLE MODELS FOR YOUR KEY ===")
for c in chat_models:
    print(c)
