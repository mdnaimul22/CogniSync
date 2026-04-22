"""Pass 4 — Consolidation (LLM, only for slug conflicts)."""

import json
import logging
import re
from pathlib import Path

from src.providers import LLMProvider
from src.schema import KnowledgeCandidate
from src.services.ki_writer import load_ki, slugify, update_ki, write_ki

logger = logging.getLogger(__name__)


def _parse_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"([\{].*[\}])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def pass4_consolidate(
    llm: LLMProvider,
    prompts_dir: Path,
    knowledge_dir: Path,
    project: str,
    candidate: KnowledgeCandidate,
    conv_id: str,
) -> None:
    """Merge a conflicting candidate with the existing KI via LLM."""
    slug = slugify(candidate.slug)
    existing = load_ki(knowledge_dir, project, slug)

    if not existing:
        # Race condition — write directly
        write_ki(
            knowledge_dir=knowledge_dir,
            project=project,
            slug=candidate.slug,
            summary=candidate.summary,
            artifact_content=candidate.artifact,
            tags=candidate.tags,
            area=candidate.area,
            conv_id=conv_id,
        )
        return

    system = (prompts_dir / "p4_consolidate.md").read_text(encoding="utf-8")
    user_msg = (
        f"NEW:\n{candidate.summary}\n\n"
        f"EXISTING_SUMMARY:\n{existing['summary']}\n\n"
        f"EXISTING_ARTIFACT:\n{existing['artifact'][:2000]}"
    )

    raw = llm.call(system=system, user=user_msg)
    result = _parse_json(raw)

    if not isinstance(result, dict):
        logger.warning("  [P4] Bad JSON for %s — skipping consolidation", slug)
        return

    action = result.get("action", "SKIP").upper()
    logger.info("  [P4] %s: %s — %s", slug, action, result.get("reasoning", ""))

    if action == "SKIP":
        return

    new_summary = result.get("new_summary", "").strip()
    new_artifact = result.get("new_artifact", "").strip()

    if not new_summary or not new_artifact:
        logger.warning("  [P4] Empty content for %s — skipping", slug)
        return

    update_ki(existing["ki_dir"], new_summary, new_artifact, conv_id)
    logger.info("  [P4] Updated: %s", slug)
