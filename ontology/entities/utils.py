"""Shared utilities for the entities sub-package."""

from __future__ import annotations

from typing import Any


def as_list(value: Any) -> list[str]:
    """Coerce a scalar, list, or None front-matter value to a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]
