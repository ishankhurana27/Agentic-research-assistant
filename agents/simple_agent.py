# agents/simple_agent.py

from groq import Groq

class SimpleAgent:
    """
    Minimal stable wrapper for Groq LLM.
    """

    def __init__(self, model="llama-3.3-70b-versatile", system=None):
        self.model = model
        self.system = system
        self.client = Groq()

    def run(self, messages, system=None):
        final_system = system or self.system

        full_messages = []
        if final_system:
            full_messages.append({"role": "system", "content": final_system})
        full_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
        )

        # FIXED: correct format for your Groq SDK
        return response.choices[0].message.content
