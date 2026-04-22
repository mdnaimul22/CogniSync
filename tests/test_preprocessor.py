import json
from src.core import preprocess_overview

def test_preprocess_overview():
    lines = [
        json.dumps({"step_index": 0, "source": "USER_EXPLICIT", "type": "USER_INPUT",
                    "content": "<USER_REQUEST>\nHello, build me a REST API\n</USER_REQUEST>\n<ADDITIONAL_METADATA>\nCursor on line 5\n</ADDITIONAL_METADATA>"}),
        json.dumps({"step_index": 1, "source": "USER_EXPLICIT", "type": "CODE_ACKNOWLEDGEMENT",
                    "content": ""}),
        json.dumps({"step_index": 2, "source": "MODEL", "type": "PLANNER_RESPONSE",
                    "content": "Sure! I will create a FastAPI server with CRUD endpoints.",
                    "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "/home/user/projects/myapp/server.py"}}]}),
        json.dumps({"step_index": 3, "source": "USER_EXPLICIT", "type": "VIEW_FILE",
                    "content": "The user viewed file /home/user/foo.py lines 1-500 ... huge content"}),
        json.dumps({"step_index": 4, "source": "USER_EXPLICIT", "type": "USER_INPUT",
                    "content": "<USER_REQUEST>\nAdd authentication with JWT\n</USER_REQUEST>\n<ADDITIONAL_METADATA>\nMore noise\n</ADDITIONAL_METADATA>"}),
        json.dumps({"step_index": 5, "source": "MODEL", "type": "PLANNER_RESPONSE",
                    "content": "I will add JWT middleware. {{ CHECKPOINT 3 }} This is clean."}),
    ]
    raw = "\n".join(lines)
    
    turns = preprocess_overview(raw)
    
    assert len(turns) == 4
    assert turns[0].role == "user"
    assert "Hello, build me a REST API" in turns[0].text
    assert "Cursor on line 5" not in turns[0].text
    
    assert turns[1].role == "assistant"
    assert "FastAPI server" in turns[1].text
    assert "[Tools: write_to_file]" in turns[1].text
    
    assert turns[3].role == "assistant"
    assert "CHECKPOINT" not in turns[3].text
    assert "This is clean" in turns[3].text
