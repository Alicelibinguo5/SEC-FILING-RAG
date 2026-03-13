from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:
    filename: str
    page_number: int
    text: str


@dataclass(frozen=True)
class Section:
    filename: str
    title: str
    start_page: int
    end_page: int
    pages: tuple[PageText, ...]


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    filename: str
    section_title: str
    start_page: int
    end_page: int
    page_numbers: tuple[int, ...]
    chunk_index: int
    text: str
