from __future__ import annotations

from dir2tag.core import tags


def setup_function() -> None:
    # ensure a clean extractor registry for each test run
    tags.clear_extractors()
    # re-register the built-ins
    from importlib import reload

    reload(tags)


def test_words_extractor_basic() -> None:
    out = tags.folder_name_to_tags("My-Folder_name 2025")
    assert "my" in out
    assert "folder" in out
    assert "name" in out
    assert "2025" in out


def test_seven_digit_extractor() -> None:
    s = "FC2-PPV-1042868_1 - Pornhub.com.mp4"
    out = tags.folder_name_to_tags(s)
    # 1042868 is a 7-digit sequence and should appear
    assert "1042868" in out
