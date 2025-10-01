from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

VIDEO_EXTENSIONS: set[str] = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".ts",
    ".mpg",
    ".mpeg",
}


def is_video_file(path: Path) -> bool:
    """Return True if `path` is a file and has a known video suffix.

    Suffix comparison is case-insensitive.
    """
    try:
        return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    except OSError:
        # In case of permission errors or other filesystem issues, treat as not video.
        return False


def enumerate_video_files(root: Path) -> Iterator[Path]:
    """Yield Path objects for video files under ``root``.

    Args:
        root: Path pointing to a directory to scan. If ``root`` does not
            exist or is not a directory, the generator will be empty.

    Yields:
        Path: absolute Path objects for each video file found.

    Notes:
        - Uses :meth:`Path.rglob` to recursively enumerate files.
        - Does not follow symlinked directories by default (depends on
          platform semantics of rglob).

    """
    root_path = Path(root)
    if not root_path.exists() or not root_path.is_dir():
        return

    for p in root_path.rglob("*"):
        if is_video_file(p):
            yield p
