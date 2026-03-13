from __future__ import annotations

import os
from typing import Protocol

from openai import OpenAI


class EmbeddingClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class OpenAIEmbeddingClient:
    def __init__(self, model: str):
        self.model = model
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
        self.client = OpenAI(api_key=api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


class SentenceTransformerEmbeddingClient:
    def __init__(self, model: str):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=False).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]


def build_embedding_client(provider: str, model: str) -> EmbeddingClient:
    normalized = provider.strip().lower()
    if normalized == "openai":
        return OpenAIEmbeddingClient(model=model)
    if normalized == "sentence-transformers":
        return SentenceTransformerEmbeddingClient(model=model)
    raise ValueError(f"Unsupported embedding provider: {provider}")
