"""
Answer eval: does the coach follow its rules?

    python -m nutritrack.knowledge.eval_answers knowledge/answer_eval_cases.json
    python -m nutritrack.knowledge.eval_answers knowledge/answer_eval_cases.json --runs 3

Answers vary between runs, so each case checks PROPERTIES of the answer, not
exact text. Supported checks under "expect":
  contains_any   the answer mentions at least one of these (case-insensitive)
  not_contains   the answer mentions none of these
  min_sources    at least this many cited sources
  max_sources    at most this many cited sources (0 = must cite nothing)

--runs N asks every question N times. A rule the coach follows only
sometimes is a real problem, and one run can hide it.
"""

import argparse
import asyncio
import json
from pathlib import Path

from nutritrack.db.database import get_session
from nutritrack.db.schemas import CoachAnswer
from nutritrack.knowledge.coach import ask_coach


def check(expect: dict, answer: CoachAnswer) -> list[str]:
    """Return a list of failed checks (empty = pass)."""
    failures = []
    text = answer.answer.lower()
    sources = len(answer.sources)

    if "contains_any" in expect and not any(
        phrase.lower() in text for phrase in expect["contains_any"]
    ):
        failures.append(f"should mention one of {expect['contains_any']}")
    for phrase in expect.get("not_contains", []):
        if phrase.lower() in text:
            failures.append(f'should not mention "{phrase}"')
    if "min_sources" in expect and sources < expect["min_sources"]:
        failures.append(
            f"should cite at least {expect['min_sources']} source(s), cited {sources}"
        )
    if "max_sources" in expect and sources > expect["max_sources"]:
        failures.append(
            f"should cite at most {expect['max_sources']} source(s), cited {sources}"
        )
    return failures


async def run_eval(cases_path: Path, runs: int) -> None:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    passed = 0
    total = 0

    for case in cases:
        for run in range(1, runs + 1):
            with get_session() as session:
                answer = await ask_coach(case["question"], session)
            failures = check(case["expect"], answer)
            total += 1
            label = f"{case['name']}" + (f" (run {run})" if runs > 1 else "")

            if failures:
                print(f"FAIL  {label}")
                for failure in failures:
                    print(f"      - {failure}")
                print(f"      answer: {answer.answer}")
            else:
                passed += 1
                print(f"PASS  {label}")

    print(f"\n{passed}/{total} passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()
    asyncio.run(run_eval(args.cases, args.runs))
