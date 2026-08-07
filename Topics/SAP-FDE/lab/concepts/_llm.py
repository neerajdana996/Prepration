"""Shared helper: build the Gemini chat model from your .env.

Every concept file imports get_llm() from here so the setup lives in one place.
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_llm(temperature: float = 0.0, **kwargs) -> ChatGoogleGenerativeAI:
    """Return a configured Gemini chat model.

    temperature: 0.0 = deterministic-ish (knob hard-left), 1.0 = creative (knob right).
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your-free-key-here":
        raise SystemExit(
            "\n  No API key found.\n"
            "  1) Copy .env.example to .env\n"
            "  2) Get a FREE key at https://aistudio.google.com/apikey\n"
            "  3) Paste it as GOOGLE_API_KEY in .env\n"
        )
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    return ChatGoogleGenerativeAI(
        model=model, temperature=temperature, google_api_key=api_key, **kwargs
    )
