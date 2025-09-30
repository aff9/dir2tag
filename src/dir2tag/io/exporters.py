from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping


def write_jsonl(records: Iterable[Mapping[str, object]], path: Path) -> None:
    """Write an iterable of mapping records to `path` in JSONL format.

    Writes with UTF-8 encoding and ensure_ascii=False to preserve unicode.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write("\n")
