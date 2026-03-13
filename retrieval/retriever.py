from __future__ import annotations

from pathlib import Path

import chromadb

from ingestion.embeddings import EmbeddingClient
from retrieval.schemas import RetrievedChunk


class FilingRetriever:
    def __init__(self, chroma_dir: Path, collection_name: str, embedding_client: EmbeddingClient):
        self.client = chromadb.PersistentClient(path=str(chroma_dir))
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception as exc:
            raise FileNotFoundError(
                f"Chroma collection '{collection_name}' was not found in {chroma_dir}. "
                "Run `python -m ingestion.ingest` first."
            ) from exc
        self.embedding_client = embedding_client

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_embedding = self.embedding_client.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            RetrievedChunk(
                text=document,
                filename=metadata["filename"],
                section_title=metadata["section_title"],
                start_page=int(metadata["start_page"]),
                end_page=int(metadata["end_page"]),
                page_numbers=parse_page_numbers(metadata["page_numbers"]),
                chunk_index=int(metadata["chunk_index"]),
                distance=float(distance),
            )
            for document, metadata, distance in zip(documents, metadatas, distances, strict=True)
        ]


def parse_page_numbers(value: str) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(int(page) for page in value.split(","))
