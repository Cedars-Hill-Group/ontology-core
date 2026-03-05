"""Tests for the config loader."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from ontology.config import get_knowledge_base_path, get_output_path, load_config


class TestLoadConfig:
    def test_loads_valid_yaml(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(
            textwrap.dedent(
                """\
                knowledge_base:
                  path: /some/path
                output:
                  path: /some/output
                """
            ),
            encoding="utf-8",
        )
        config = load_config(cfg_file)
        assert config["knowledge_base"]["path"] == "/some/path"
        assert config["output"]["path"] == "/some/output"

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="config.yaml.example"):
            load_config(tmp_path / "missing.yaml")

    def test_empty_file_returns_empty_dict(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("", encoding="utf-8")
        config = load_config(cfg_file)
        assert config == {}


class TestGetKnowledgeBasePath:
    def test_returns_path(self, tmp_path: Path) -> None:
        config = {"knowledge_base": {"path": str(tmp_path)}}
        result = get_knowledge_base_path(config)
        assert result == tmp_path.resolve()

    def test_raises_when_path_empty(self) -> None:
        with pytest.raises(ValueError, match="knowledge_base.path"):
            get_knowledge_base_path({"knowledge_base": {"path": ""}})

    def test_raises_when_key_missing(self) -> None:
        with pytest.raises(ValueError, match="knowledge_base.path"):
            get_knowledge_base_path({})


class TestGetOutputPath:
    def test_custom_output_path(self, tmp_path: Path) -> None:
        config = {"output": {"path": str(tmp_path / "out")}}
        result = get_output_path(config)
        assert result == (tmp_path / "out").resolve()

    def test_default_output_path(self) -> None:
        result = get_output_path({})
        assert result.name == "output"
