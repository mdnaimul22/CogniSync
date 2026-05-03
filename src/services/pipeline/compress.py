"""Pass 1 — Compression.

Compresses raw dialogue into a dense, searchable summary.
"""

from src.providers import LLMProvider
from src.config import Settings, setup_logger, read_text, exists

logger = setup_logger(Settings.LOG_DIR / "service.log", "daemon.services.pipeline.compress")


def pass1_compress(llm: LLMProvider, prompts_dir_rel: str, raw_dialogue: str) -> str | None:
    """Compress raw dialogue into a short dense summary.

    Returns None when the conversation has no meaningful content.
    """
    prompt_path = f"{prompts_dir_rel}/p1_compress.md"
    if not exists(prompt_path):
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    system = read_text(prompt_path)
    result = llm.call(system=system, user=raw_dialogue)

    if not result or result.strip() == "-" or len(result.split()) < 10:
        logger.info("  [P1] Below threshold — skipping")
        return None

    logger.info("  [P1] Compressed to %d words", len(result.split()))
    return result
