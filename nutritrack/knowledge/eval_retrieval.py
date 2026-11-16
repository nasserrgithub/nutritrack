"""
Retrieval eval: does search find the passage that answers each question?

    python -m nutritrack.knowledge.eval_retrieval knowledge/eval_cases.json
    python -m nutritrack.knowledge.eval_retrieval knowledge/eval_cases.json --k 1

A case is a HIT if one of the top-k chunks comes from the expected source and
contains one of the expected phrases.

recall@k: share of questions whose passage is in the top k.
MRR (mean reciprocal rank): 1.0 if a correct passage is always ranked first,
0.5 if always second, etc. Rewards ranking it higher, not just finding it.

Before scoring, every phrase is checked against the stored chunks. A phrase
that appears nowhere (a typo, or text changed by cleaning) could never be
found, so it's reported as a broken test instead of counting as a search miss.
"""

import argparse
import asyncio
import json
from pathlib import Path

from nutritrack.ai.embeddings import embed_query
from nutritrack.db.database import get_session
from nutritrack.db.models import KnowledgeChunkModel
from nutritrack.db.repositories import KnowledgeRepository


def normalize(text: str) -> str:
    """Lowercase, single spaces, and plain hyphens instead of – and —."""
    text = text.replace("–", "-").replace("—", "-")
    return " ".join(text.lower().split())


def case_phrases(case: dict) -> list[str]:
    """Accepts either "must_contain_any": [...] or a single "must_contain": "..."."""
    phrases = case.get("must_contain_any") or [case.get("must_contain", "")]
    phrases = [normalize(p) for p in phrases if p and p.strip()]
    if not phrases:
        # An empty phrase would be "found" in every chunk and always pass
        raise ValueError(f"Case has no phrases: {case['question']}")
    return phrases


def find_broken_phrases(cases: list[dict]) -> list[str]:
    """Phrases that don't appear in ANY stored chunk of their source."""
    with get_session() as session:
        chunks = session.query(KnowledgeChunkModel).all()
        contents_by_source: dict[str, list[str]] = {}
        for chunk in chunks:
            contents_by_source.setdefault(chunk.source.slug, []).append(
                normalize(chunk.content)
            )

    problems = []
    for case in cases:
        contents = contents_by_source.get(case["source"], [])
        if not contents:
            problems.append(f"unknown source '{case['source']}' in: {case['question']}")
            continue
        for phrase in case_phrases(case):
            if not any(phrase in content for content in contents):
                problems.append(f'"{phrase}" not found in {case["source"]} ({case["question"]})')
    return problems


async def run_eval(cases_path: Path, k: int) -> None:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    problems = find_broken_phrases(cases)
    if problems:
        print("Broken test cases (fix these first, they can never pass):")
        for problem in problems:
            print(f"  - {problem}")
        return

    hits = 0
    reciprocal_ranks: list[float] = []

    for case in cases:
        query_vector = await embed_query(case["question"])
        with get_session() as session:
            results = KnowledgeRepository(session).search(query_vector, k=k)
            found = [(chunk.source.slug, normalize(chunk.content)) for chunk, _ in results]

        phrases = case_phrases(case)
        rank = next(
            (
                i + 1
                for i, (slug, content) in enumerate(found)
                if slug == case["source"] and any(p in content for p in phrases)
            ),
            None,
        )

        if rank:
            hits += 1
            reciprocal_ranks.append(1 / rank)
            print(f"HIT  (rank {rank})  {case['question']}")
        else:
            reciprocal_ranks.append(0.0)
            print(f"MISS            {case['question']}")

    print(f"\nrecall@{k}: {hits}/{len(cases)} = {hits / len(cases):.0%}")
    print(f"MRR: {sum(reciprocal_ranks) / len(cases):.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    asyncio.run(run_eval(args.cases, args.k))