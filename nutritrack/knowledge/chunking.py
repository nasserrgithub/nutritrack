"""
Split a document into chunks for retrieval.

Rules:
  1. Split into paragraphs at blank lines.
  2. Never mix sections: a new heading always starts a new chunk.
  3. Pack paragraphs together until a chunk reaches about max_tokens.
  4. Split paragraphs that are too long at sentence boundaries, never mid-sentence.
  5. Put the section heading at the top of each chunk, so it keeps its context.
"""

import math
import re

HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")  # "# Title", "## Section", ...
SENTENCE_END_RE = re.compile(
    r"(?<=[.!?])\s+(?=[A-Z0-9])"
)  # after . ! ? before a new sentence


def estimate_tokens(text: str) -> int:
    """Rough rule of thumb for English: about 4 characters per token."""
    return math.ceil(len(text) / 4)


def split_long_paragraph(paragraph: str, max_tokens: int) -> list[str]:
    """Split a paragraph that's too big into pieces, at sentence boundaries."""
    pieces: list[str] = []
    current = ""
    for sentence in SENTENCE_END_RE.split(paragraph):
        candidate = f"{current} {sentence}".strip()
        if current and estimate_tokens(candidate) > max_tokens:
            pieces.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def chunk_text(text: str, max_tokens: int = 400) -> list[str]:
    """Split a document into chunks of at most ~max_tokens, never crossing a heading."""
    chunks: list[str] = []
    heading: str | None = None
    current: list[str] = []

    def close_chunk() -> None:
        if current:
            body = "\n\n".join(current)
            chunks.append(f"{heading}\n\n{body}" if heading else body)
            current.clear()

    for block in text.split("\n\n"):
        block = " ".join(block.split())  # collapse line breaks and extra spaces
        if not block:
            continue

        match = HEADING_RE.match(block)
        if match:
            close_chunk()  # a new section starts: finish the old chunk
            heading = match.group(1)
            continue

        pieces = (
            split_long_paragraph(block, max_tokens)
            if estimate_tokens(block) > max_tokens
            else [block]
        )
        for piece in pieces:
            if current and estimate_tokens("\n\n".join(current + [piece])) > max_tokens:
                close_chunk()  # adding this piece would make the chunk too big
            current.append(piece)

    close_chunk()  # the last chunk
    return chunks
