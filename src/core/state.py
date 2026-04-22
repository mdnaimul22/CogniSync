"""Persistent state tracking for Daemon processes."""

import json
import logging
from pathlib import Path

from src.schema import DaemonState

logger = logging.getLogger(__name__)


def load_state(state_file: Path) -> DaemonState:
    """Load daemon state (processed conversations)."""
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            return DaemonState(**data)
        except Exception as exc:
            logger.warning("Could not load state from %s: %s", state_file, exc)
    return DaemonState()


def save_state(state_file: Path, state: DaemonState) -> None:
    """Save daemon state."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(state.model_dump_json(indent=4), encoding="utf-8")
