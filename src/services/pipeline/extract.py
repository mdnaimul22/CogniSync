"""Pass 2 — Dual extraction (memories + solutions) run in parallel."""

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.providers.llm import LLMProvider
from src.schema.models import SolutionExtract

logger = logging.getLogger(__name__)


def _parse_json(text: str) -> list | dict | None:
    """Extract and parse JSON from LLM response robustly."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*([\[\{].*?[\]\}])\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    match = re.search(r"([\[\{].*[\]\}])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def _extract_memories(llm: LLMProvider, prompts_dir: Path, compressed: str) -> list[str]:
    system = (prompts_dir / "p2_memories.md").read_text(encoding="utf-8")
    raw = llm.call(system=system, user=f"Conversation summary:\n\n{compressed}")
    result = _parse_json(raw)
    if not isinstance(result, list):
        return []
    return [str(m) for m in result if m]


def _extract_solutions(llm: LLMProvider, prompts_dir: Path, compressed: str) -> list[SolutionExtract]:
    system = (prompts_dir / "p2_solutions.md").read_text(encoding="utf-8")
    raw = llm.call(system=system, user=f"Conversation summary:\n\n{compressed}")
    result = _parse_json(raw)
    if not isinstance(result, list):
        return []
    valid: list[SolutionExtract] = []
    for s in result:
        if isinstance(s, dict) and s.get("slug") and s.get("problem") and s.get("solution"):
            valid.append(SolutionExtract(**s))
    return valid


def pass2_extract(
    llm: LLMProvider,
    prompts_dir: Path,
    compressed: str,
) -> tuple[list[str], list[SolutionExtract]]:
    """Run memories and solutions extraction in parallel.

    Returns (memories, solutions). Both empty → pipeline stops.
    """
    memories: list[str] = []
    solutions: list[SolutionExtract] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_mem = executor.submit(_extract_memories, llm, prompts_dir, compressed)
        fut_sol = executor.submit(_extract_solutions, llm, prompts_dir, compressed)
        for fut in as_completed([fut_mem, fut_sol]):
            if fut is fut_mem:
                memories = fut.result()
                logger.info("  [P2a] %d factual memories", len(memories))
            else:
                solutions = fut.result()
                logger.info("  [P2b] %d solutions", len(solutions))

    return memories, solutions
