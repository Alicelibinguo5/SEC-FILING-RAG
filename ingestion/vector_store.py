from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from ingestion.schemas import Chunk


class ChromaVectorStore:
    def __init__(self, persist_directory: Path, collection_name: str):
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection: Collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    "filename": chunk.filename,
                    "section_title": chunk.section_title,
                    "start_page": chunk.start_page,
                    "end_page": chunk.end_page,
                    "page_numbers": ",".join(str(page) for page in chunk.page_numbers),
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in chunks
            ],
        )

    def count(self) -> int:
        return self.collection.count()
