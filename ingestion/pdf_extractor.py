from __future__ import annotations

from pathlib import Path

import fitz

from ingestion.schemas import PageText


def extract_pdf_pages(pdf_path: Path) -> list[PageText]:
    pages: list[PageText] = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if not text:
                continue
            pages.append(
                PageText(
                    filename=pdf_path.name,
                    page_number=page_index,
                    text=normalize_whitespace(text),
                )
            )
    return pages


def load_all_pdfs(pdf_dir: Path) -> list[PageText]:
    all_pages: list[PageText] = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        all_pages.extend(extract_pdf_pages(pdf_path))
    return all_pages


def normalize_whitespace(text: str) -> str:
    normalized_lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in normalized_lines if line)
