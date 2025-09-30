"""Convenience runner for Stage1.

Run as: python main.py <root>
This mirrors the behavior of ``python -m tree2tag`` for Stage1.
"""
from __future__ import annotations

import sys
from pathlib import Path
from tree2tag.core.paths import enumerate_video_files


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if not argv:
        print("Usage: python main.py <root>")
        return 2

    root = Path(argv[0])
    for p in enumerate_video_files(root):
        try:
            print(p.relative_to(root))
        except Exception:
            print(p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
