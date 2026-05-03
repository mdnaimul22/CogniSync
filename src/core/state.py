"""Persistent state tracking for Daemon processes."""

import json
from src.schema import DaemonState
from src.config import Settings, setup_logger, exists, read_text, write_text, ensure_dir

logger = setup_logger(Settings.LOG_DIR / "core.log", "daemon.core.state")


def load_state(state_file_path: str) -> DaemonState:
    """Load daemon state (processed conversations)."""
    if exists(state_file_path):
        try:
            data = json.loads(read_text(state_file_path))
            return DaemonState(**data)
        except Exception as exc:
            logger.warning("Could not load state from %s: %s", state_file_path, exc)
    return DaemonState()


def save_state(state_file_path: str, state: DaemonState) -> None:
    """Save daemon state."""
    # Derive parent dir
    parent = state_file_path.rsplit("/", 1)[0] if "/" in state_file_path else ""
    if parent:
        ensure_dir(parent)
    write_text(state_file_path, state.model_dump_json(indent=4))
