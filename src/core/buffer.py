"""Dialogue buffering logic for turning bytes into turns."""

import time
from threading import Lock
from .preprocessor import build_dialogue, parse_line
from src.helpers import detect_project, mask_sensitive_data
from src.schema import DialogueTurn
from src.config import Settings, setup_logger, get_abs_path, exists, get_size, read_from_pos


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
        self.abs_path = overview_path # Keeping the name for compatibility, but it's the string passed
        self.buffer_turns = buffer_turns
        self.buffer_timeout = buffer_timeout
        self.file_pos: int = get_size(self.path_rel) if exists(self.path_rel) else 0
        self.turns: list[DialogueTurn] = []
        self.last_flush: float = time.time()
        self.raw_text: str = ""
        self._lock = Lock()

    def ingest_new_lines(self) -> None:
        """Read newly appended bytes and parse turns."""
        with self._lock:
            try:
                if not exists(self.path_rel):
                    return
                size = get_size(self.path_rel)
                if size <= self.file_pos:
                    return
                
                new_data = read_from_pos(self.path_rel, self.file_pos)
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
