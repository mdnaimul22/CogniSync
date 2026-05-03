"""Pass 3 — Slug match (no LLM).

Splits candidates into new (write directly) vs existing (needs consolidation).
"""

from src.schema.models import KnowledgeCandidate
from src.services.ki_writer import ki_exists, slugify
from src.config import Settings, setup_logger

logger = setup_logger(Settings.LOG_DIR / "service.log", "daemon.services.pipeline.slug_match")


def pass3_slug_match(
    knowledge_dir_rel: str,
    project: str,
    candidates: list[KnowledgeCandidate],
) -> tuple[list[KnowledgeCandidate], list[KnowledgeCandidate]]:
    """Split candidates into new and existing by slug lookup.

    Returns (to_create, to_consolidate).
    """
    to_create: list[KnowledgeCandidate] = []
    to_consolidate: list[KnowledgeCandidate] = []

    for candidate in candidates:
        slug = slugify(candidate.slug)
        if ki_exists(knowledge_dir_rel, project, slug):
            to_consolidate.append(candidate)
            logger.info("  [P3] EXISTS: %s", slug)
        else:
            to_create.append(candidate)
            logger.info("  [P3] NEW:    %s", slug)

    return to_create, to_consolidate
