from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    pdf_dir: Path = Path(os.getenv("PDF_DIR", "./data/pdfs"))
    chroma_dir: Path = Path(os.getenv("CHROMA_DIR", "./chroma_db"))
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "sec_filings")
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "openai")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
    chunk_size_tokens: int = 500
    chunk_overlap_tokens: int = 100
    top_k: int = 5


def get_settings() -> Settings:
    return Settings()
