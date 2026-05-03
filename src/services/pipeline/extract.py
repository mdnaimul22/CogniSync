"""Pass 2 — Dual extraction (memories + solutions) run in parallel."""

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.providers.llm import LLMProvider
from src.schema.models import SolutionExtract
from src.config import Settings, setup_logger, read_text

logger = setup_logger(Settings.LOG_DIR / "service.log", "daemon.services.pipeline.extract")


def _parse_json(text: str) -> list | dict | None:
    """Extract and parse JSON from LLM response robustly."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.debug("Initial JSON parse failed, falling back to regex")


    match = re.search(r"```(?:json)?\s*([\[\{].*?[\]\}])\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logger.debug(f"P2 JSON regex block parse failed: {e}")

    match = re.search(r"([\[\{].*[\]\}])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logger.debug(f"P2 JSON broad regex parse failed: {e}")
            
    return None


def _extract_memories(llm: LLMProvider, prompts_dir_rel: str, compressed: str) -> list[str]:
    system = read_text(f"{prompts_dir_rel}/p2_memories.md")
    raw = llm.call(system=system, user=f"Conversation summary:\n\n{compressed}")
    result = _parse_json(raw)
    if not isinstance(result, list):
        return []
    return [str(m) for m in result if m]


def _extract_solutions(llm: LLMProvider, prompts_dir_rel: str, compressed: str) -> list[SolutionExtract]:
    system = read_text(f"{prompts_dir_rel}/p2_solutions.md")
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
    prompts_dir_rel: str,
    compressed: str,
) -> tuple[list[str], list[SolutionExtract]]:
    """Run memories and solutions extraction in parallel.

    Returns (memories, solutions). Both empty → pipeline stops.
    """
    memories: list[str] = []
    solutions: list[SolutionExtract] = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        fut_mem = executor.submit(_extract_memories, llm, prompts_dir_rel, compressed)
        fut_sol = executor.submit(_extract_solutions, llm, prompts_dir_rel, compressed)
        for fut in as_completed([fut_mem, fut_sol]):
            if fut is fut_mem:
                memories = fut.result()
                logger.info("  [P2a] %d factual memories", len(memories))
            else:
                solutions = fut.result()
                logger.info("  [P2b] %d solutions", len(solutions))

    return memories, solutions
