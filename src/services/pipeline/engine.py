"""Pipeline engine — orchestrates the 4 passes.

Pass 1: Compress raw dialogue → dense summary
Pass 2: Extract memories + solutions (parallel)
Pass 3: Slug match against existing KIs (no LLM)
Pass 4: Consolidate conflicts (LLM, only when needed)
"""

import logging
from pathlib import Path

from src.services.pipeline.compress import pass1_compress
from src.services.pipeline.consolidate import pass4_consolidate
from src.services.pipeline.extract import pass2_extract
from src.services.pipeline.slug_match import pass3_slug_match
from src.config import Settings
from src.providers.llm import LLMProvider
from src.schema.models import KnowledgeCandidate, PipelineResult, SolutionExtract
from src.services.ki_writer import write_ki

logger = logging.getLogger(__name__)

_SEP = "─" * 50


def _build_candidates(
    memories: list[str],
    solutions: list[SolutionExtract],
    project: str,
) -> list[KnowledgeCandidate]:
    """Convert Pass 2 outputs into a unified KnowledgeCandidate list."""
    candidates: list[KnowledgeCandidate] = []

    if memories:
        artifact = f"# {project.title()} — Context Notes\n\n## Facts\n"
        artifact += "".join(f"- {m}\n" for m in memories)
        candidates.append(KnowledgeCandidate(
            slug=f"{project}-context",
            summary=" | ".join(memories[:5])[:500],
            artifact=artifact,
            tags=["context", "facts", project],
            area="main",
        ))

    for sol in solutions:
        artifact = (
            f"# {sol.problem}\n\n"
            f"## Problem\n{sol.problem}\n\n"
            f"## Solution\n{sol.solution}\n"
        )
        candidates.append(KnowledgeCandidate(
            slug=sol.slug,
            summary=f"Problem: {sol.problem[:200]} | Solution: {sol.solution[:200]}",
            artifact=artifact,
            tags=sol.tags + ["solution"],
            area="solutions",
        ))

    return candidates


def run_pipeline(
    settings: Settings,
    raw_dialogue: str,
    conv_id: str,
    project: str,
) -> PipelineResult:
    """Full 4-pass pipeline. Returns PipelineResult with created/consolidated counts."""
    llm = LLMProvider(
        base_url=Settings.LLM_BASE_URL,
        api_key=Settings.LLM_API_KEY,
        model=Settings.LLM_MODEL,
    )
    knowledge_dir = Settings.KNOWLEDGE_DIR
    prompts_dir = Settings.PROMPTS_DIR
    result = PipelineResult()

    logger.info(_SEP)
    logger.info("Pipeline | conv=%s… | project=%s", conv_id[:8], project)

    # Pass 1 — Compress
    compressed = pass1_compress(llm, prompts_dir, raw_dialogue)
    if not compressed:
        logger.info("  [STOP] Nothing meaningful in conversation")
        logger.info(_SEP)
        return result

    # Pass 2 — Extract (parallel)
    memories, solutions = pass2_extract(llm, prompts_dir, compressed)
    if not memories and not solutions:
        logger.info("  [STOP] Nothing worth saving")
        logger.info(_SEP)
        return result

    # Build typed candidates
    candidates = _build_candidates(memories, solutions, project)

    # Pass 3 — Slug match
    to_create, to_consolidate = pass3_slug_match(knowledge_dir, project, candidates)

    # Write new KIs directly
    for c in to_create:
        write_ki(
            knowledge_dir=knowledge_dir,
            project=project,
            slug=c.slug,
            summary=c.summary,
            artifact_content=c.artifact,
            tags=c.tags,
            area=c.area,
            conv_id=conv_id,
        )
        logger.info("  [WRITE] %s/%s", project, c.slug)
        result.created += 1

    # Pass 4 — Consolidate conflicts
    for c in to_consolidate:
        pass4_consolidate(llm, prompts_dir, knowledge_dir, project, c, conv_id)
        result.consolidated += 1

    logger.info("  [DONE] %d KI(s) written/updated", result.total)
    logger.info(_SEP)
    return result
