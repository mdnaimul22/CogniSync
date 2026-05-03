import json
import shutil
from pathlib import Path

from src.services.ki_writer import slugify, write_ki, ki_exists, load_ki, update_ki

def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("This is a--test_with__spaces") == "this-is-a-test-with-spaces"
    assert slugify("---trim---") == "trim"

def test_ki_writer(tmp_path: Path):
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    
    # Use absolute strings for the test since ki_writer uses _abs() internally
    knowledge_dir_str = str(knowledge_dir)
    project = "testproj"
    slug = "Test Candidate 1"
    summary = "This is a summary"
    artifact = "# Content\nHello"
    tags = ["test", "mock"]
    area = "main"
    conv_id = "12345"
    
    # 1. Write
    ki_dir_str = write_ki(knowledge_dir_str, project, slug, summary, artifact, tags, area, conv_id)
    
    assert Path(ki_dir_str).exists()
    assert ki_exists(knowledge_dir_str, project, slug)
    
    # 2. Load
    loaded = load_ki(knowledge_dir_str, project, slug)
    assert loaded is not None
    assert loaded["summary"] == summary
    assert loaded["artifact"] == artifact
    assert loaded["metadata"]["version"] == 1
    
    # 3. Update
    new_summary = "Updated summary"
    new_artifact = "Updated artifact"
    update_ki(ki_dir_str, new_summary, new_artifact, "67890")
    
    loaded2 = load_ki(knowledge_dir_str, project, slug)
    assert loaded2 is not None
    assert loaded2["summary"] == new_summary
    assert loaded2["artifact"] == new_artifact
    assert loaded2["metadata"]["version"] == 2
    assert len(loaded2["metadata"]["references"]) == 2
