from __future__ import annotations

from ingestion.config import get_settings
from ingestion.embeddings import build_embedding_client
from retrieval.generator import AnswerGenerator
from retrieval.retriever import FilingRetriever
from retrieval.schemas import RetrievedChunk


class FilingQAService:
    def __init__(self):
        settings = get_settings()
        embedding_client = build_embedding_client(
            provider=settings.embedding_provider,
            model=settings.embedding_model,
        )
        self.retriever = FilingRetriever(
            chroma_dir=settings.chroma_dir,
            collection_name=settings.chroma_collection,
            embedding_client=embedding_client,
        )
        self.generator = AnswerGenerator(model=settings.chat_model)
        self.top_k = settings.top_k

    def answer_question(self, question: str) -> tuple[str, list[RetrievedChunk]]:
        chunks = self.retriever.retrieve(question, top_k=self.top_k)
        answer = self.generator.generate(question, chunks)
        return answer, chunks
