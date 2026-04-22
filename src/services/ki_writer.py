"""Knowledge Item persistence layer.

Writes and updates KI files under knowledge/<project>/<slug>/:
    metadata.json
    timestamps.json
    artifacts/summary.md
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(text: str) -> str:
    """Convert any string to a valid KI slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_ki(
    knowledge_dir: Path,
    project: str,
    slug: str,
    summary: str,
    artifact_content: str,
    tags: list[str],
    area: str,
    conv_id: str,
) -> Path:
    """Create a new KI under knowledge/<project>/<slug>/. Returns the KI directory."""
    slug = slugify(slug)
    ki_dir = knowledge_dir / project / slug
    artifacts_dir = ki_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    now = _now()

    metadata = {
        "summary": summary,
        "tags": tags,
        "area": area,
        "project": project,
        "created_at": now,
        "modified_at": now,
        "version": 1,
        "references": [{"type": "conversation", "id": conv_id}],
    }
    (ki_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    timestamps = {"created": now, "modified": now, "accessed": now}
    (ki_dir / "timestamps.json").write_text(
        json.dumps(timestamps, indent=4), encoding="utf-8"
    )

    (artifacts_dir / "summary.md").write_text(artifact_content, encoding="utf-8")

    return ki_dir


def update_ki(ki_dir: Path, new_summary: str, new_artifact: str, conv_id: str) -> None:
    """Update an existing KI. Increments version, appends reference."""
    now = _now()

    meta_path = ki_dir / "metadata.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    metadata["summary"] = new_summary
    metadata["modified_at"] = now
    metadata["version"] = metadata.get("version", 1) + 1

    refs = metadata.get("references", [])
    if not any(r.get("id") == conv_id for r in refs):
        refs.append({"type": "conversation", "id": conv_id})
    metadata["references"] = refs

    meta_path.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    ts_path = ki_dir / "timestamps.json"
    timestamps = json.loads(ts_path.read_text(encoding="utf-8")) if ts_path.exists() else {}
    timestamps["modified"] = now
    ts_path.write_text(json.dumps(timestamps, indent=4), encoding="utf-8")

    artifacts_dir = ki_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    (artifacts_dir / "summary.md").write_text(new_artifact, encoding="utf-8")


def ki_exists(knowledge_dir: Path, project: str, slug: str) -> bool:
    """Check if a KI already exists."""
    ki_dir = knowledge_dir / project / slugify(slug)
    return (ki_dir / "metadata.json").exists()


def load_ki(knowledge_dir: Path, project: str, slug: str) -> dict | None:
    """Load existing KI data. Returns None if not found."""
    ki_dir = knowledge_dir / project / slugify(slug)
    meta_path = ki_dir / "metadata.json"
    artifact_path = ki_dir / "artifacts" / "summary.md"

    if not meta_path.exists():
        return None

    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    artifact = artifact_path.read_text(encoding="utf-8") if artifact_path.exists() else ""

    return {
        "ki_dir": ki_dir,
        "metadata": metadata,
        "summary": metadata.get("summary", ""),
        "artifact": artifact,
    }
