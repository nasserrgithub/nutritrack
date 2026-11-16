import re

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from nutritrack.ai.client import answer_from_sources
from nutritrack.ai.embeddings import embed_query
from nutritrack.api.dependencies import get_current_user, get_db_session
from nutritrack.core.logger import get_logger
from nutritrack.db.models import UserModel
from nutritrack.db.repositories import KnowledgeRepository
from nutritrack.db.schemas import CoachAnswer, CoachQuestion, CoachSource

logger = get_logger(__name__)
router = APIRouter()

TOP_K = 5  # your eval showed the right passage is always in the top 5


@router.post("/ask", response_model=CoachAnswer)
async def ask_coach(
    body: CoachQuestion,
    user: UserModel = Depends(get_current_user),  # only logged-in users
    session: Session = Depends(get_db_session),
) -> CoachAnswer:
    # 1. Retrieve
    query_vector = await embed_query(body.question)
    results = KnowledgeRepository(session).search(query_vector, k=TOP_K)
    passages = [
        {"number": i, "title": chunk.source.title, "url": chunk.source.url, "content": chunk.content}
        for i, (chunk, _distance) in enumerate(results, 1)
    ]

    # 2 + 3. Augment and generate
    answer = await answer_from_sources(body.question, passages)

    # Return only the passages Claude actually cited
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    sources = [
        CoachSource(number=p["number"], title=p["title"], url=p["url"], excerpt=p["content"][:300])
        for p in passages
        if p["number"] in cited
    ]
    logger.info(f"Coach question answered with {len(sources)} cited sources")
    return CoachAnswer(answer=answer, sources=sources)