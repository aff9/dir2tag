from __future__ import annotations

import os
from pathlib import Path

from tree2tag.core.paths import enumerate_video_files


def test_enumerate_video_files(tmp_path: Path) -> None:
    # Create a small directory tree with video and non-video files
    (tmp_path / "sub").mkdir()
    video1 = tmp_path / "a.mp4"
    video1.write_text("x")
    video2 = tmp_path / "sub" / "b.mkv"
    video2.write_text("y")
    non_video = tmp_path / "c.txt"
    non_video.write_text("z")

    found = sorted(str(p.relative_to(tmp_path)) for p in enumerate_video_files(tmp_path))
    assert found == ["a.mp4", os.path.join("sub", "b.mkv")]


def test_enumerate_with_nonexistent_root(tmp_path: Path) -> None:
    # point to a path that does not exist
    missing = tmp_path / "nope"
    found = list(enumerate_video_files(missing))
    assert found == []
