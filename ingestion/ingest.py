from __future__ import annotations

from ingestion.chunker import TokenChunker
from ingestion.config import get_settings
from ingestion.embeddings import build_embedding_client
from ingestion.pdf_extractor import load_all_pdfs
from ingestion.section_detector import detect_sections
from ingestion.vector_store import ChromaVectorStore


def run_ingestion(reset_collection: bool = True) -> int:
    settings = get_settings()
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    settings.pdf_dir.mkdir(parents=True, exist_ok=True)

    pages = load_all_pdfs(settings.pdf_dir)
    if not pages:
        raise FileNotFoundError(f"No PDF files found in {settings.pdf_dir}")

    sections = detect_sections(pages)
    if not sections:
        raise ValueError("No filing sections were detected from the provided PDFs")

    chunker = TokenChunker(
        chunk_size_tokens=settings.chunk_size_tokens,
        chunk_overlap_tokens=settings.chunk_overlap_tokens,
    )
    chunks = chunker.chunk_sections(sections)
    if not chunks:
        raise ValueError("No text chunks were created from the provided PDFs")

    embedding_client = build_embedding_client(
        provider=settings.embedding_provider,
        model=settings.embedding_model,
    )
    embeddings = embedding_client.embed_texts([chunk.text for chunk in chunks])

    store = ChromaVectorStore(
        persist_directory=settings.chroma_dir,
        collection_name=settings.chroma_collection,
    )
    if reset_collection and store.count() > 0:
        store.reset()
    store.add_chunks(chunks, embeddings)
    return len(chunks)


if __name__ == "__main__":
    total_chunks = run_ingestion(reset_collection=True)
    print(f"Ingestion complete. Indexed {total_chunks} chunks.")
