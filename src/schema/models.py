from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class DialogueTurn(BaseModel):
    """A single parsed turn from overview.txt."""

    role: Literal["user", "assistant"]
    text: str
    step: int = 0


class KnowledgeCandidate(BaseModel):
    """A candidate KI ready for slug-match and persistence."""

    slug: str
    summary: str
    artifact: str
    tags: list[str] = Field(default_factory=list)
    area: str = "main"


class SolutionExtract(BaseModel):
    """A problem→solution pair extracted by Pass 2b."""

    slug: str
    problem: str
    solution: str
    tags: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    """Outcome of a full pipeline run."""

    created: int = 0
    consolidated: int = 0

    @property
    def total(self) -> int:
        return self.created + self.consolidated


class DaemonState(BaseModel):
    """Persistent state tracking processed conversations."""

    processed: list[str] = Field(default_factory=list)
