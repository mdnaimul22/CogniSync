"""Dialogue preprocessor — parses overview.txt JSON lines into DialogueTurn objects.

Extracted from watcher.py:66-106. Uses schema models instead of raw dicts.
"""

import json
import re

from typing import Optional

from src.schema import DialogueTurn

_SKIP_TYPES: frozenset[str] = frozenset({
    "CODE_ACKNOWLEDGEMENT",
    "VIEW_FILE",
    "FILE_VIEWER_RESPONSE",
    "FILE_CHANGE_RESPONSE",
    "TOOL_RESULT",
})

_RE_USER_REQUEST = re.compile(r"<USER_REQUEST>(.*?)</USER_REQUEST>", re.DOTALL)
_RE_META = re.compile(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", re.DOTALL)
_RE_EPHEMERAL = re.compile(r"<EPHEMERAL_MESSAGE>.*?</EPHEMERAL_MESSAGE>", re.DOTALL)
_RE_CHECKPOINT = re.compile(r"\{\{\s*CHECKPOINT.*?\}\}", re.DOTALL)


def parse_line(line: str) -> Optional[DialogueTurn]:
    """Parse a single JSON line from overview.txt into a DialogueTurn.

    Returns None if the line is noise/irrelevant.
    """
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None

    stype = obj.get("type", "")
    src = obj.get("source", "")
    content = obj.get("content", "")
    step = obj.get("step_index", 0)

    if stype in _SKIP_TYPES:
        return None

    if stype == "USER_INPUT" and src == "USER_EXPLICIT":
        m = _RE_USER_REQUEST.search(content)
        text = m.group(1).strip() if m else _RE_META.sub("", content).strip()
        if text:
            return DialogueTurn(role="user", text=text, step=step)

    if stype == "PLANNER_RESPONSE" and src == "MODEL":
        text = _RE_CHECKPOINT.sub("", content)
        text = _RE_EPHEMERAL.sub("", text).strip()
        tool_calls: list[dict] = obj.get("tool_calls") or []
        if tool_calls:
            names = [tc.get("name", "?") for tc in tool_calls]
            text += f"\n[Tools: {', '.join(names)}]"
        if text:
            return DialogueTurn(role="assistant", text=text, step=step)

    return None


def build_dialogue(turns: list[DialogueTurn]) -> str:
    """Format a list of DialogueTurns into a single dialogue string."""
    parts: list[str] = []
    for t in turns:
        prefix = "USER:" if t.role == "user" else "AI:"
        parts.append(f"{prefix} {t.text}")
    return "\n\n".join(parts)


def preprocess_overview(raw_text: str) -> list[DialogueTurn]:
    """Parse raw overview.txt content into a clean list of DialogueTurns."""
    turns: list[DialogueTurn] = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        turn = parse_line(line)
        if turn:
            turns.append(turn)
    return turns
