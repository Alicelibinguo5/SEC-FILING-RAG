from __future__ import annotations

import hashlib

import tiktoken

from ingestion.schemas import Chunk, Section


class TokenChunker:
    def __init__(self, chunk_size_tokens: int = 500, chunk_overlap_tokens: int = 100):
        if chunk_overlap_tokens >= chunk_size_tokens:
            raise ValueError("chunk_overlap_tokens must be smaller than chunk_size_tokens")
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_sections(self, sections: list[Section]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for section in sections:
            chunks.extend(self._chunk_section(section))
        return chunks

    def _chunk_section(self, section: Section) -> list[Chunk]:
        page_token_spans: list[tuple[int, int, int]] = []
        all_tokens: list[int] = []

        for page in section.pages:
            page_text = flatten_page_text(page.text)
            if not page_text:
                continue
            page_tokens = self.encoding.encode(page_text)
            if not page_tokens:
                continue

            start = len(all_tokens)
            all_tokens.extend(page_tokens)
            end = len(all_tokens)
            page_token_spans.append((page.page_number, start, end))

            separator_tokens = self.encoding.encode("\n\n")
            all_tokens.extend(separator_tokens)

        if not page_token_spans:
            return []

        stride = self.chunk_size_tokens - self.chunk_overlap_tokens
        chunks: list[Chunk] = []
        chunk_index = 0

        for start in range(0, len(all_tokens), stride):
            token_window = all_tokens[start : start + self.chunk_size_tokens]
            chunk_text = self.encoding.decode(token_window).strip()
            if not chunk_text:
                continue

            covered_pages = pages_for_window(
                page_token_spans=page_token_spans,
                window_start=start,
                window_end=start + len(token_window),
            )
            if not covered_pages:
                continue

            chunks.append(
                Chunk(
                    chunk_id=build_chunk_id(
                        filename=section.filename,
                        section_title=section.title,
                        start_page=covered_pages[0],
                        end_page=covered_pages[-1],
                        chunk_index=chunk_index,
                        text=chunk_text,
                    ),
                    filename=section.filename,
                    section_title=section.title,
                    start_page=covered_pages[0],
                    end_page=covered_pages[-1],
                    page_numbers=tuple(covered_pages),
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )
            chunk_index += 1

            if start + self.chunk_size_tokens >= len(all_tokens):
                break

        return chunks


def flatten_page_text(text: str) -> str:
    return " ".join(text.split())


def pages_for_window(
    page_token_spans: list[tuple[int, int, int]],
    window_start: int,
    window_end: int,
) -> list[int]:
    return [
        page_number
        for page_number, page_start, page_end in page_token_spans
        if page_start < window_end and page_end > window_start
    ]


def build_chunk_id(
    filename: str,
    section_title: str,
    start_page: int,
    end_page: int,
    chunk_index: int,
    text: str,
) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    normalized_title = section_title.lower().replace(" ", "-")
    return f"{filename}-{normalized_title}-p{start_page}-{end_page}-c{chunk_index}-{digest}"
