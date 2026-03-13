from __future__ import annotations

import os

from openai import OpenAI

from retrieval.schemas import RetrievedChunk


SYSTEM_PROMPT = """You answer questions about NVIDIA 10-K filings.
Use only the provided context. If the answer is not supported by the context, say so.
Every substantive claim must include citations in the format [filename p.X] or [filename pp.X-Y].
Be concise and specific."""


def build_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        blocks.append(
            f"Source {index}\n"
            f"File: {chunk.filename}\n"
            f"Section: {chunk.section_title}\n"
            f"Pages: {format_pages(chunk)}\n"
            f"Content: {chunk.text}"
        )
    return "\n\n".join(blocks)


def format_pages(chunk: RetrievedChunk) -> str:
    if chunk.start_page == chunk.end_page:
        return str(chunk.start_page)
    return f"{chunk.start_page}-{chunk.end_page}"


class AnswerGenerator:
    def __init__(self, model: str):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for answer generation")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> str:
        context = build_context(chunks)
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Context:\n{context}\n\n"
                        "Answer using only the context. Include citations for each claim."
                    ),
                },
            ],
        )
        return response.output_text.strip()
