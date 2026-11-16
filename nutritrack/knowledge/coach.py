"""
The RAG coach pipeline: retrieve → augment → generate.

Used by the API endpoint AND by the answer eval, so the eval tests exactly
the code users hit.
"""

import re

from sqlalchemy.orm import Session

from nutritrack.ai.client import answer_from_sources
from nutritrack.ai.embeddings import embed_query
from nutritrack.ai.prompts import Passage
from nutritrack.db.repositories import KnowledgeRepository
from nutritrack.db.schemas import CoachAnswer, CoachSource

TOP_K = 5  # the retrieval eval showed the right passage is always in the top 5
CITATION_RE = re.compile(r"\[(\d+)\]")


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

    # Return only the passages Claude actually cited
    cited = {int(n) for n in CITATION_RE.findall(answer)}
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
