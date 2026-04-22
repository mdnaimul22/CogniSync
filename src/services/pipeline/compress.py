"""Pass 1 — Compression.

Compresses raw dialogue into a dense, searchable summary.
"""

import logging

from src.providers import LLMProvider

logger = logging.getLogger(__name__)


def pass1_compress(llm: LLMProvider, prompts_dir, raw_dialogue: str) -> str | None:
    """Compress raw dialogue into a short dense summary.

    Returns None when the conversation has no meaningful content.
    """
    from pathlib import Path

    prompt_path = Path(prompts_dir) / "p1_compress.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    system = prompt_path.read_text(encoding="utf-8")
    result = llm.call(system=system, user=raw_dialogue)

    if not result or result.strip() == "-" or len(result.split()) < 10:
        logger.info("  [P1] Below threshold — skipping")
        return None

    logger.info("  [P1] Compressed to %d words", len(result.split()))
    return result
