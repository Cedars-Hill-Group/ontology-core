"""Load user-defined action/function registries from JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class UserDefinitionRegistry:
    """Catalog-like loader for user-managed actions and functions."""

    def __init__(self, directory: str | Path) -> None:
        self._directory = Path(directory)

    def load(self, name: str) -> dict[str, Any]:
        """Load a definition catalog by file stem.

        Expected path: `<directory>/<name>.json`
        """
        target = self._directory / f"{name}.json"
        if not target.exists():
            raise FileNotFoundError(f"Definition catalog not found: {target}")
        data = json.loads(target.read_text(encoding="utf-8"))
        if "$schema_version" not in data:
            raise ValueError(f"Definition catalog missing $schema_version: {target}")
        return data

    def load_actions(self) -> dict[str, Any]:
        """Load `actions.json`."""
        return self.load("actions")

    def load_functions(self) -> dict[str, Any]:
        """Load `functions.json`."""
        return self.load("functions")
