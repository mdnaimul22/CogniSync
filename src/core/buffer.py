"""Dialogue buffering logic for turning bytes into turns."""

import time
import os
from threading import Lock

from .preprocessor import build_dialogue, parse_line
from src.helpers import detect_project, mask_sensitive_data
from src.schema import DialogueTurn
from src.config import Settings, setup_logger, get_abs_path

logger = setup_logger(Settings.LOG_DIR / "core.log", "daemon.core.buffer")


class ConvBuffer:
    """Tracks file position and buffered turns for one conversation."""

    def __init__(
        self,
        overview_path: str,
        buffer_turns: int,
        buffer_timeout: int,
    ) -> None:
        self.path_rel = overview_path
        self.abs_path = get_abs_path(overview_path)
        self.buffer_turns = buffer_turns
        self.buffer_timeout = buffer_timeout
        self.file_pos: int = os.path.getsize(self.abs_path) if os.path.exists(self.abs_path) else 0
        self.turns: list[DialogueTurn] = []
        self.last_flush: float = time.time()
        self.raw_text: str = ""
        self._lock = Lock()

    def ingest_new_lines(self) -> None:
        """Read newly appended bytes and parse turns."""
        with self._lock:
            try:
                if not os.path.exists(self.abs_path):
                    return
                size = os.path.getsize(self.abs_path)
                if size <= self.file_pos:
                    return
                with open(self.abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(self.file_pos)
                    new_data = f.read()
                self.file_pos = size
                self.raw_text += new_data
                for line in new_data.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    turn = parse_line(line)
                    if turn:
                        self.turns.append(turn)
            except Exception as exc:
                logger.warning("  Ingest error: %s", exc)

    def should_flush(self) -> bool:
        if not self.turns:
            return False
        if len(self.turns) >= self.buffer_turns:
            return True
        if time.time() - self.last_flush >= self.buffer_timeout:
            return True
        return False

    def flush(self) -> tuple[str, str]:
        """Return (masked_dialogue, project) and reset buffer."""
        with self._lock:
            dialogue = build_dialogue(self.turns)
            project = detect_project(self.raw_text)
            self.turns = []
            self.last_flush = time.time()
            self.raw_text = ""
        return mask_sensitive_data(dialogue), project
