"""
Ingest documents into the knowledge base: extract → chunk → embed → store.

    python -m nutritrack.knowledge.ingest knowledge/sources.json
"""

import asyncio
import json
import sys
from pathlib import Path

from nutritrack.ai.embeddings import embed_documents
from nutritrack.core.logger import get_logger, setup_logging
from nutritrack.db.database import get_session
from nutritrack.db.repositories import KnowledgeRepository
from nutritrack.knowledge.chunking import chunk_text
from nutritrack.knowledge.extract import extract_text

logger = get_logger(__name__)


async def ingest(manifest_path: Path) -> None:
    sources = json.loads(manifest_path.read_text(encoding="utf-8"))

    for source in sources:
        path = manifest_path.parent / source["file"]
        if not path.exists():
            logger.warning(f"[{source['slug']}] file not found, skipping: {path}")
            continue

        text = extract_text(path)
        chunks = chunk_text(text, max_tokens=400)

        # Embed each chunk WITH its document title, so a passage like
        # "the RDA is 0.8 g/kg/day" also carries "this is about protein and exercise"
        vectors = await embed_documents([f"{source['title']}\n\n{c}" for c in chunks])

        # Embedding is slow and happens over the network, so it's done
        # before opening the database transaction, not inside it
        with get_session() as session:
            KnowledgeRepository(session).replace_source(
                slug=source["slug"],
                title=source["title"],
                url=source["url"],
                chunks=list(zip(chunks, vectors)),
            )
        logger.info(f"[{source['slug']}] ingested {len(chunks)} chunks")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(ingest(Path(sys.argv[1])))