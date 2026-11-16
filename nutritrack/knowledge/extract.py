"""
Turn source files into plain text the chunker can split.

PDFs need cleaning before chunking. Each rule below removes something that
would be stored and searched like real guidance, but isn't:
  - title, author list and affiliations before the Abstract
  - running headers and footers repeated on every page ("Page 3 of 25")
  - back matter: references, funding, author details...
  - words hyphenated across line breaks ("vege- tarian")
  - symbols pypdf can't decode ("/C15") and citation numbers ("[116, 142]")
"""

import re
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

# Start of the content: skip the title, author list and affiliations above it
START_RE = re.compile(r"^\s*abstract\b", re.IGNORECASE)

# First back-matter heading: everything after it is not guidance
END_RE = re.compile(
    r"^\s*(abbreviations|acknowledg(e)?ments|funding|competing interests|"
    r"authors?'? contributions|author details|availability of data.*|references|bibliography)\s*$",
    re.IGNORECASE,
)


def _shape(line: str) -> str:
    """A line with its numbers replaced, so 'Page 3 of 25' and 'Page 4 of 25' match."""
    return re.sub(r"\d+", "#", line.strip())


def _join_lines(lines: list[str]) -> str:
    text = " ".join(lines)
    # Rejoin words hyphenated across line breaks: "vege- tarian" → "vegetarian"
    # but keep real hyphens before "and", "or", "to": "pre- and postexercise"
    text = re.sub(r"(\w)- (?!(?:and|or|to)\b)(\w)", r"\1\2", text)
    # Remove symbols pypdf couldn't decode, like "/C15"
    text = re.sub(r"/C\d+\s*", "", text)
    # Remove citation numbers like "[12]", "[116, 142]" or "[3–5]"
    text = re.sub(r"\s*\[\d+(?:\s*[,–-]\s*\d+)*\]", "", text)
    return text


def extract_pdf(path: Path) -> str:
    reader = PdfReader(path)
    pages = [(page.extract_text() or "").splitlines() for page in reader.pages]

    # Running headers and footers: lines with the same shape on most pages
    shape_counts = Counter(
        shape
        for lines in pages
        for shape in {_shape(line) for line in lines if line.strip()}
    )
    min_pages = max(3, len(pages) // 2)
    repeated = {shape for shape, count in shape_counts.items() if count >= min_pages}

    # Documents without an "Abstract" line are kept from the start
    has_abstract = any(START_RE.match(line) for lines in pages for line in lines)
    started = not has_abstract

    kept: list[str] = []
    for lines in pages:
        for line in lines:
            if not started:
                started = bool(START_RE.match(line))
                if not started:
                    continue
            # Stop at the back matter: references, funding, author details...
            if END_RE.match(line):
                return _join_lines(kept)
            if line.strip() and _shape(line) not in repeated:
                kept.append(line.strip())
    return _join_lines(kept)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    if suffix in {".md", ".txt"}:
        return path.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported file type: {path.name}")