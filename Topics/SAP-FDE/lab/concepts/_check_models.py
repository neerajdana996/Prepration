"""Diagnostic: list the Gemini models your API key can actually use.

Run:  uv run python concepts/_check_models.py
Then set GEMINI_MODEL in .env to one of the printed chat models (e.g. gemini-2.5-flash),
and EMBED_MODEL to an embedding model (e.g. models/text-embedding-004).
"""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

print("Models available to your key:\n")
for m in client.models.list():
    actions = getattr(m, "supported_actions", None)
    print(f"  {m.name}   {actions if actions else ''}")
