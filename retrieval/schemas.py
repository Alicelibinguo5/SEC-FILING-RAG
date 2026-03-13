from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    filename: str
    section_title: str
    start_page: int
    end_page: int
    page_numbers: tuple[int, ...]
    chunk_index: int
    distance: float
