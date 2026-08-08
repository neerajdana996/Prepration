"""Shared helper: build the Gemini chat model from your .env.
AIzaSyAzxxgwrREFEMNbvwWO6k3Wb5UbNZHBOnQ

Every concept file imports get_llm() from here so the setup lives in one place.
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()


def get_llm(temperature: float = 0.0, **kwargs) -> ChatGoogleGenerativeAI:
    """Return a configured Gemini chat model.

    temperature: 0.0 = deterministic-ish (knob hard-left), 1.0 = creative (knob right).
    """
    # Simple fallback check to assist developer workspace setups
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key == "your-free-key-here":
        raise SystemExit(
            "\n  No API key found.\n"
            "  1) Copy .env.example to .env\n"
            "  2) Get a FREE key at https://google.com\n"
            "  3) Paste it as GEMINI_API_KEY or GOOGLE_API_KEY in .env\n"
        )
        
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Modern ChatGoogleGenerativeAI relies on the native environment variables smoothly.
    # Passing api_key here targets the new SDK layer correctly.
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        **kwargs
    )


def get_embeddings(model: str | None = None) -> GoogleGenerativeAIEmbeddings:
    """Gemini embedding model. Same api_key-alias fix as get_llm (see module docstring)."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your-free-key-here":
        raise SystemExit("Set GOOGLE_API_KEY (or GEMINI_API_KEY) in .env")
    return GoogleGenerativeAIEmbeddings(
        model=model or os.getenv("EMBED_MODEL", "models/gemini-embedding-001"),
        api_key=api_key,  # alias! not google_api_key
    )
