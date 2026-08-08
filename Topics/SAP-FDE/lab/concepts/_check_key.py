"""Diagnostic: is your key a valid AI Studio API key, and is it sent correctly?

Bypasses langchain AND the google SDK — calls the REST endpoint directly with
the key as ?key=... (the correct transport for an API key). This isolates
'bad key' from 'SDK mis-sending the key'.

Run:  uv run python concepts/_check_key.py
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

k = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
print(f"key detected: prefix={k[:4]!r}  length={len(k)}")
print("(a valid AI Studio key starts with 'AIza' and is ~39 chars, no quotes/spaces)\n")

resp = requests.get(
    "https://generativelanguage.googleapis.com/v1beta/models", params={"key": k}
)
print(f"REST status: {resp.status_code}")
print(resp.text[:400])
