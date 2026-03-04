"""Configuration loader for ontology-core.

Reads ``config.yaml`` from the repository root.  The file is excluded from
version control (see ``.gitignore``); copy ``config.yaml.example`` and update
the paths before running any collection commands.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _REPO_ROOT / "config.yaml"


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and return the YAML configuration.

    Parameters
    ----------
    config_path:
        Explicit path to a YAML config file.  When *None* the loader looks for
        ``config.yaml`` in the repository root.

    Returns
    -------
    dict
        Parsed configuration dictionary.

    Raises
    ------
    FileNotFoundError
        When the config file cannot be found.
    """
    path = Path(config_path) if config_path is not None else _DEFAULT_CONFIG_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            "Copy config.yaml.example to config.yaml and update the paths."
        )

    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    return data


def get_knowledge_base_path(config: dict[str, Any] | None = None) -> Path:
    """Return the resolved path to the knowledge-base root directory."""
    if config is None:
        config = load_config()
    raw = config.get("knowledge_base", {}).get("path", "")
    if not raw:
        raise ValueError("knowledge_base.path is not set in config.yaml")
    return Path(os.path.expandvars(os.path.expanduser(raw))).resolve()


def get_output_path(config: dict[str, Any] | None = None) -> Path:
    """Return the resolved path to the output directory."""
    if config is None:
        config = load_config()
    raw = config.get("output", {}).get("path", "output")
    return Path(os.path.expandvars(os.path.expanduser(raw))).resolve()
