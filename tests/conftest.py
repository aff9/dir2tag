from __future__ import annotations

import sys
from pathlib import Path


def _add_src_to_path() -> None:
    # Insert project 'src' directory to sys.path so tests can import packages
    # using the src/ layout (works for local test runs and CI).
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


_add_src_to_path()
