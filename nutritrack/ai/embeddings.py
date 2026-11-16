"""
Embeddings with Voyage AI (voyage-4).

Rules that keep search working:
  - Use the SAME model for passages and questions.
  - Mark passages as input_type="document" and questions as input_type="query".
"""

import voyageai

from nutritrack.api.settings import get_settings
from nutritrack.core.exceptions import AIServiceError
from nutritrack.core.logger import get_logger
from nutritrack.db.models import EMBEDDING_DIM

logger = get_logger(__name__)
settings = get_settings()

EMBEDDING_MODEL = "voyage-4"
BATCH_SIZE = 64  # texts per request, well under Voyage's limits

_client: voyageai.AsyncClient | None = None


def _get_client() -> voyageai.AsyncClient:
    """Create the client on first use, so importing this module never needs a key."""
    global _client
    if _client is None:
        api_key = settings.voyage_api_key.get_secret_value()
        if not api_key:
            raise AIServiceError("VOYAGE_API_KEY is not set")
        _client = voyageai.AsyncClient(api_key=api_key, max_retries=3)
    return _client


async def _embed(texts: list[str], input_type: str) -> list[list[float]]:
    client = _get_client()
    vectors: list[list[float]] = []
    total_tokens = 0
    try:
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]
            result = await client.embed(
                batch, model=EMBEDDING_MODEL, input_type=input_type
            )
            vectors.extend([[float(x) for x in vector] for vector in result.embeddings])
            total_tokens += result.total_tokens
    except Exception as exc:
        raise AIServiceError(f"Embedding request failed: {exc}") from exc

    if vectors and len(vectors[0]) != EMBEDDING_DIM:
        raise AIServiceError(
            f"Expected {EMBEDDING_DIM}-number vectors, got {len(vectors[0])}"
        )

    logger.info(
        f"Embedded {len(texts)} {input_type}(s) with {EMBEDDING_MODEL} ({total_tokens} tokens)"
    )
    return vectors


async def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed passages for storing."""
    if not texts:
        return []
    return await _embed(texts, input_type="document")


async def embed_query(text: str) -> list[float]:
    """Embed a user's question for searching."""
    return (await _embed([text], input_type="query"))[0]
