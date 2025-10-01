"""Convenience runner for Stage1.

Run as: python main.py <root>
This mirrors the behavior of ``python -m dir2tag`` for Stage1.
"""

# ruff: noqa: E402
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from pathlib import Path as _Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

# Ensure src/ is on sys.path so the package can be imported when running
# `uv run main.py ...` from the repository root.
_project_root = _Path(__file__).resolve().parents[0]
_src = str(_project_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


from dir2tag.core.paths import enumerate_video_files
from dir2tag.core.tags import folder_name_to_tags
from dir2tag.io.exporters import write_jsonl


def _iter_records(
    root: Path,
    include_filename: bool = False,
) -> Iterable[Mapping[str, object]]:
    for p in enumerate_video_files(root):
        rel = None
        try:
            rel = p.relative_to(root)
        except Exception:
            rel = p

        folder = str(rel.parent) if rel.parent else ""
        tags = folder_name_to_tags(folder)
        if include_filename:
            tags += folder_name_to_tags(p.name)

        yield {"relative_path": str(rel), "tags": tags}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="dir2tag runner")
    parser.add_argument("root", metavar="ROOT_DIR", help="root directory to scan")
    parser.add_argument(
        "-o",
        "--jsonl",
        metavar="JSONL_PATH",
        help="write JSONL to PATH",
        default=None,
    )
    parser.add_argument(
        "--include-filename",
        help="also include filename tokens as tags",
        action="store_true",
    )
    args = parser.parse_args(argv)

    root = Path(args.root)

    if args.jsonl:
        write_jsonl(
            _iter_records(root, include_filename=args.include_filename),
            Path(args.jsonl),
        )
    else:
        for rec in _iter_records(root, include_filename=args.include_filename):
            print(rec["relative_path"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
