"""Orchestrator Service — coordinates preprocessor, watcher, and pipeline.

The fan-in point where core rules and service providers converge.
"""

import logging
import sys
from pathlib import Path

from src.config import Settings
from src.core import build_dialogue, preprocess_overview, load_state, save_state
from src.helpers.detection import detect_project
from src.helpers.masking import mask_sensitive_data
from src.services.pipeline.engine import run_pipeline

logger = logging.getLogger(__name__)


def process_conversation(settings: Settings, conv_id: str) -> None:
    """Force process a specific conversation from raw overview file."""
    overview = Settings.BRAIN_DIR / conv_id / ".system_generated" / "logs" / "overview.txt"

    if not overview.exists():
        logger.error("Overview file not found: %s", overview)
        sys.exit(1)

    raw_text = overview.read_text(encoding="utf-8", errors="ignore")
    turns = preprocess_overview(raw_text)

    if not turns:
        logger.info("No turns to process.")
        return

    dialogue = build_dialogue(turns)
    dialogue = mask_sensitive_data(dialogue)
    project = detect_project(raw_text)

    try:
        result = run_pipeline(Settings, dialogue, conv_id, project)
        logger.info("Processed %s. Created: %d, Consolidated: %d", conv_id, result.created, result.consolidated)

        state = load_state(Settings.STATE_FILE)
        if conv_id not in state.processed:
            state.processed.append(conv_id)
            save_state(Settings.STATE_FILE, state)
    except Exception as exc:
        logger.error("Pipeline failed for %s: %s", conv_id, exc)
        sys.exit(1)


def process_buffered_dialogue(settings: Settings, conv_id: str, dialogue: str, project: str) -> None:
    """Process a dialogue string that was buffered by the watcher."""
    try:
        result = run_pipeline(Settings, dialogue, conv_id, project)
        logger.info("Processed %s. Created: %d, Consolidated: %d", conv_id, result.created, result.consolidated)

        state = load_state(Settings.STATE_FILE)
        if conv_id not in state.processed:
            state.processed.append(conv_id)
            save_state(Settings.STATE_FILE, state)
    except Exception as exc:
        logger.error("Pipeline error [%s]: %s", conv_id[:8], exc)


def start_daemon(settings: Settings, main_logger: logging.Logger, run_once: bool = False) -> None:
    """Start the real-time file watcher."""
    from src.services.watcher import start_watcher
    start_watcher(Settings, main_logger, run_once=run_once)
