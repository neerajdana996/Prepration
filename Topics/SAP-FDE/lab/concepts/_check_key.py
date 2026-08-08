"""Diagnostic: show BOTH key env vars so we can see which is the good AIza key.

Run:  uv run python concepts/_check_key.py
"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
    k = os.getenv(name) or ""
    good = k.startswith("AIza")
    print(f"{name}: prefix={k[:4]!r} length={len(k)} {'<- looks valid (AIza)' if good else '<- NOT an AI Studio key' if k else '<- (unset)'}")
    if k:
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models", params={"key": k}
        )
        print(f"   REST status when used: {r.status_code}")
