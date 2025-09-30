from __future__ import annotations

from pathlib import Path
from dir2tag.io.exporters import write_jsonl
import json


def test_write_jsonl(tmp_path: Path) -> None:
    out = tmp_path / "out.jsonl"
    records = [
        {"relative_path": "a.mp4", "tags": ["foo", "bar"]},
        {"relative_path": "sub/b.mkv", "tags": ["baz"]},
    ]
    write_jsonl(records, out)

    text = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(text) == 2
    loaded = [json.loads(line) for line in text]
    assert loaded == records
