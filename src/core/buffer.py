"""Dialogue buffering logic for turning bytes into turns."""

import logging
import time
from pathlib import Path
from threading import Lock

from .preprocessor import build_dialogue, parse_line
from src.helpers import detect_project, mask_sensitive_data
from src.schema import DialogueTurn


class ConvBuffer:
    """Tracks file position and buffered turns for one conversation."""

    def __init__(
        self,
        overview_path: Path,
        buffer_turns: int,
        buffer_timeout: int,
        logger: logging.Logger,
    ) -> None:
        self.path = overview_path
        self.buffer_turns = buffer_turns
        self.buffer_timeout = buffer_timeout
        self._logger = logger
        self.file_pos: int = overview_path.stat().st_size  # tail from current end
        self.turns: list[DialogueTurn] = []
        self.last_flush: float = time.time()
        self.raw_text: str = ""
        self._lock = Lock()

    def ingest_new_lines(self) -> None:
        """Read newly appended bytes and parse turns."""
        with self._lock:
            try:
                size = self.path.stat().st_size
                if size <= self.file_pos:
                    return
                with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
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
                self._logger.warning("  Ingest error: %s", exc)

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
