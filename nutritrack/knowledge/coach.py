"""
The RAG coach pipeline: retrieve → augment → generate → check.

Used by the API endpoint AND by the answer eval, so the eval tests exactly
the code users hit.
"""

import re

from sqlalchemy.orm import Session

from nutritrack.ai.client import answer_from_sources
from nutritrack.ai.embeddings import embed_query
from nutritrack.ai.prompts import Passage
from nutritrack.core.logger import get_logger
from nutritrack.db.repositories import KnowledgeRepository
from nutritrack.db.schemas import CoachAnswer, CoachSource

logger = get_logger(__name__)

TOP_K = 5  # the retrieval eval showed the right passage is always in the top 5
CITATION = r"\[\d+(?:\s*,\s*\d+)*\]"  # [1] or [1, 2]
CITATION_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
# Fixed sentences from the prompt that are allowed without a citation:
# they're the app's own messages, not facts from the passages.
ALLOWED_UNCITED = {
    "I don't have a source that covers that.",
    "Please talk to your doctor or a registered dietitian about what's right for you.",
}


def split_sentences(paragraph: str) -> list[str]:
    """Split into sentences, keeping citations written after the full stop
    with their sentence: "...per day. [1][2] Next" -> "...per day [1][2]." """
    normalized = re.sub(rf"([.!?])\s*((?:{CITATION})+)", r" \2\1", paragraph.strip())
    return [s for s in re.split(r"(?<=[.!?])\s+", normalized) if s]


def drop_uncited_sentences(answer: str) -> tuple[str, list[str]]:
    """
    Remove sentences without a citation from a sourced answer.
    Answers with no citations at all (the "no source" reply, medical referrals)
    are returned unchanged: they're uncited by design.
    """
    if not CITATION_RE.search(answer):
        return answer, []

    dropped: list[str] = []
    paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", answer.strip()):
        kept = []
        for sentence in split_sentences(paragraph):
            if re.search(CITATION, sentence) or sentence.strip() in ALLOWED_UNCITED:
                kept.append(sentence)
            else:
                dropped.append(sentence)
        if kept:
            paragraphs.append(" ".join(kept))
    return "\n\n".join(paragraphs), dropped


async def ask_coach(question: str, session: Session, k: int = TOP_K) -> CoachAnswer:
    # 1. Retrieve
    query_vector = await embed_query(question)
    results = KnowledgeRepository(session).search(query_vector, k=k)
    passages: list[Passage] = [
        {
            "number": i,
            "title": chunk.source.title,
            "url": chunk.source.url,
            "content": chunk.content,
        }
        for i, (chunk, _distance) in enumerate(results, 1)
    ]

    # 2 + 3. Augment and generate
    answer = await answer_from_sources(question, passages)

    # 4. Check: remove any sentence that doesn't point to a source
    answer, dropped = drop_uncited_sentences(answer)
    if dropped:
        logger.info(f"Removed {len(dropped)} uncited sentence(s): {dropped}")

    # Return only the passages Claude actually cited
    cited = {
        int(number)
        for group in CITATION_RE.findall(answer)
        for number in group.split(",")
    }
    sources = [
        CoachSource(
            number=p["number"],
            title=p["title"],
            url=p["url"],
            excerpt=p["content"][:300],
        )
        for p in passages
        if p["number"] in cited
    ]
    return CoachAnswer(answer=answer, sources=sources)
