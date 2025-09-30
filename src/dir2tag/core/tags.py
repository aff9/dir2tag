from __future__ import annotations

import re
from typing import Callable, Iterable, List

Extractor = Callable[[str], Iterable[str]]


_EXTRACTORS: List[Extractor] = []


def register_extractor(fn: Extractor) -> Extractor:
    """Register an extractor function and return it (decorator-friendly)."""
    _EXTRACTORS.append(fn)
    return fn


def clear_extractors() -> None:
    """Clear all registered extractors (useful for tests)."""
    _EXTRACTORS.clear()


def folder_name_to_tags(name: str) -> List[str]:
    """Convert a folder name into a list of tags using registered extractors.

    The function runs each extractor in registration order and accumulates
    tags. Duplicates are removed while preserving order.
    """
    seen: set[str] = set()
    out: list[str] = []
    for extractor in _EXTRACTORS:
        for t in extractor(name):
            if not t:
                continue
            if t in seen:
                continue
            seen.add(t)
            out.append(t)
    return out


# --- Built-in extractors ---


@register_extractor
def words_extractor(name: str) -> Iterable[str]:
    """Split on common delimiters and normalize words to lowercase.

    Example: "FC2-PPV-1042868_1 - Pornhub.com.mp4" -> ["fc2", "ppv", "1042868_1", "pornhub.com.mp4"]
    This extractor is intentionally conservative: it doesn't remove numbers or
    punctuation (another extractor can post-process them).
    """
    # split on spaces, hyphens, underscores
    parts = re.split(r"[\s_\-]+", name)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        yield p.lower()


@register_extractor
def seven_digit_id_extractor(name: str) -> Iterable[str]:
    """Extract 7-digit sequences from the name and yield them as tags.

    This extractor is an example of an extensible rule (for FC2 IDs or similar).
    It finds contiguous runs of 7 digits.
    """
    for m in re.finditer(r"(\d{7})", name):
        yield m.group(1)
