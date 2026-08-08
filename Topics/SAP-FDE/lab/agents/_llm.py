"""Shared Gemini helpers for the agents lab (self-contained).

api_key-alias fix (langchain-google-genai v4): pass `api_key=` (the alias);
`google_api_key=` is silently dropped and causes a 401.
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()


def _key() -> str:
    k = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not k or k == "your-free-key-here":
        raise SystemExit("Set GOOGLE_API_KEY in lab/.env (https://aistudio.google.com/apikey)")
    return k


def get_llm(temperature: float = 0.0, **kwargs) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=temperature,
        api_key=_key(),
        **kwargs,
    )


def get_embeddings(model: str | None = None) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=model or os.getenv("EMBED_MODEL", "models/gemini-embedding-001"),
        api_key=_key(),
    )
