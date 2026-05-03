"""Knowledge Item persistence layer.

Writes and updates KI files under knowledge/<project>/<slug>/:
    metadata.json
    timestamps.json
    artifacts/summary.md
"""

import json
import re
from datetime import datetime, timezone
from src.config import Settings, exists, read_text, write_text, write_json, read_json, ensure_dir


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
    knowledge_dir_rel: str,
    project: str,
    slug: str,
    summary: str,
    artifact_content: str,
    tags: list[str],
    area: str,
    conv_id: str,
) -> str:
    """Create a new KI under knowledge/<project>/<slug>/. Returns the KI directory relative path."""
    slug = slugify(slug)
    ki_dir = f"{knowledge_dir_rel}/{project}/{slug}"
    artifacts_dir = f"{ki_dir}/artifacts"
    ensure_dir(artifacts_dir)

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
    write_json(f"{ki_dir}/metadata.json", metadata)

    timestamps = {"created": now, "modified": now, "accessed": now}
    write_json(f"{ki_dir}/timestamps.json", timestamps)

    write_text(f"{artifacts_dir}/summary.md", artifact_content)

    return ki_dir


def update_ki(ki_dir_rel: str, new_summary: str, new_artifact: str, conv_id: str) -> None:
    """Update an existing KI. Increments version, appends reference."""
    now = _now()

    meta_path = f"{ki_dir_rel}/metadata.json"
    metadata = read_json(meta_path)
    metadata["summary"] = new_summary
    metadata["modified_at"] = now
    metadata["version"] = metadata.get("version", 1) + 1

    refs = metadata.get("references", [])
    if not any(r.get("id") == conv_id for r in refs):
        refs.append({"type": "conversation", "id": conv_id})
    metadata["references"] = refs

    write_json(meta_path, metadata)

    ts_path = f"{ki_dir_rel}/timestamps.json"
    timestamps = read_json(ts_path) if exists(ts_path) else {}
    timestamps["modified"] = now
    write_json(ts_path, timestamps)

    artifacts_dir = f"{ki_dir_rel}/artifacts"
    ensure_dir(artifacts_dir)
    write_text(f"{artifacts_dir}/summary.md", new_artifact)


def ki_exists(knowledge_dir_rel: str, project: str, slug: str) -> bool:
    """Check if a KI already exists."""
    ki_dir = f"{knowledge_dir_rel}/{project}/{slugify(slug)}"
    return exists(f"{ki_dir}/metadata.json")


def load_ki(knowledge_dir_rel: str, project: str, slug: str) -> dict | None:
    """Load existing KI data. Returns None if not found."""
    ki_dir = f"{knowledge_dir_rel}/{project}/{slugify(slug)}"
    meta_path = f"{ki_dir}/metadata.json"
    artifact_path = f"{ki_dir}/artifacts/summary.md"

    if not exists(meta_path):
        return None

    metadata = read_json(meta_path)
    artifact = read_text(artifact_path) if exists(artifact_path) else ""

    return {
        "ki_dir": ki_dir,
        "metadata": metadata,
        "summary": metadata.get("summary", ""),
        "artifact": artifact,
    }
