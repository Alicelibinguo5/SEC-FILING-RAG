from __future__ import annotations

import re

from ingestion.schemas import PageText, Section


ITEM_HEADING_RE = re.compile(
    r"^(item\s+(?:1a|1b|1|2|3|4|5|6|7a|7|8|9a|9b|9c|9|10|11|12|13|14|15|16)\.?\s+.+)$",
    re.IGNORECASE,
)
GENERIC_HEADING_RE = re.compile(r"^[A-Z][A-Za-z0-9,&()/' -]{2,80}$")

KNOWN_SECTION_ALIASES = {
    "risk factors",
    "management's discussion and analysis",
    "results of operations",
    "revenue",
    "business",
    "properties",
    "legal proceedings",
    "market for registrant's common stock",
}


def detect_sections(pages: list[PageText]) -> list[Section]:
    if not pages:
        return []

    sections: list[Section] = []
    pages_by_file: dict[str, list[PageText]] = {}
    for page in pages:
        pages_by_file.setdefault(page.filename, []).append(page)

    for file_pages in pages_by_file.values():
        sections.extend(detect_sections_for_file(file_pages))

    return sections


def detect_sections_for_file(pages: list[PageText]) -> list[Section]:
    sections: list[Section] = []
    current_title = "Introduction"
    current_pages: list[PageText] = []

    for page in pages:
        heading = find_section_heading(page.text)
        if heading and current_pages:
            sections.append(build_section(page_group=current_pages, title=current_title))
            current_pages = []
            current_title = heading
        elif heading:
            current_title = heading
        current_pages.append(page)

    if current_pages:
        sections.append(build_section(page_group=current_pages, title=current_title))

    return sections


def build_section(page_group: list[PageText], title: str) -> Section:
    return Section(
        filename=page_group[0].filename,
        title=title,
        start_page=page_group[0].page_number,
        end_page=page_group[-1].page_number,
        pages=tuple(page_group),
    )


def find_section_heading(page_text: str) -> str | None:
    for raw_line in page_text.splitlines():
        line = normalize_line(raw_line)
        if not line:
            continue
        if match := ITEM_HEADING_RE.match(line):
            return clean_heading(match.group(1))
        if looks_like_named_heading(line):
            return clean_heading(line)
    return None


def looks_like_named_heading(line: str) -> bool:
    lowered = line.lower()
    if lowered in KNOWN_SECTION_ALIASES:
        return True
    word_count = len(line.split())
    return (
        1 < word_count <= 8
        and GENERIC_HEADING_RE.match(line) is not None
        and line.upper() == line
    )


def clean_heading(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()
