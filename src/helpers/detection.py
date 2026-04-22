"""Project name detection from conversation logs"""

import re
from pathlib import Path


def detect_project(text: str) -> str:
    """Extract the most frequently mentioned CWD project name.

    Explicit 'CWD: /path' lines get 3x weight over '(in /path, ...)' mentions
    because the former is the actual working directory of the editor.
    Falls back to 'global' when no CWD is found.
    """
    counts: dict[str, int] = {}

    for match in re.finditer(r"CWD:\s*(/[\w/.\-]+)", text):
        name = Path(match.group(1).strip().rstrip("/")).name
        if name and name not in ("", ".", "/"):
            counts[name] = counts.get(name, 0) + 3

    for match in re.finditer(r"\(in\s+(/[\w/.\-]+),", text):
        name = Path(match.group(1).strip().rstrip("/")).name
        if name and name not in ("", ".", "/"):
            counts[name] = counts.get(name, 0) + 1

    return max(counts, key=counts.get) if counts else "global"
