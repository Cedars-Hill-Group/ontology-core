"""Markdown link and metadata reference extraction utilities."""

from __future__ import annotations

import re
from typing import Any

_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def extract_markdown_links(content: str) -> list[str]:
    """Extract local markdown links from markdown content.

    External links (http/https/mailto) are ignored.
    """
    links: list[str] = []
    for raw in _LINK_PATTERN.findall(content):
        target = raw.strip()
        lowered = target.lower()
        if lowered.startswith("http://") or lowered.startswith("https://"):
            continue
        if lowered.startswith("mailto:"):
            continue
        links.append(target)
    return links


def extract_metadata_refs(metadata: dict[str, Any]) -> list[str]:
    """Extract basic entity references from common metadata fields."""
    refs: list[str] = []
    for key in ("company", "client", "related", "links", "references"):
        value = metadata.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            refs.append(value)
            continue
        if isinstance(value, list):
            refs.extend(str(item) for item in value if item)
    return refs
