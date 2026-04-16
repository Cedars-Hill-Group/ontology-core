"""Tests for ontology release build pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ontology.build.link_extractor import extract_markdown_links, extract_metadata_refs
from ontology.build.models import BuilderConfig
from ontology.build.pipeline import OntologyReleaseBuilder, build_date_version, write_release_bundle


def test_extract_markdown_links_ignores_external() -> None:
    content = """
See [Internal](../companies/alpha-pe.md) and [Site](https://example.com) and [Mail](mailto:test@example.com)
"""
    links = extract_markdown_links(content)
    assert links == ["../companies/alpha-pe.md"]


def test_extract_metadata_refs_handles_scalars_and_lists() -> None:
    metadata = {
        "company": "Alpha PE",
        "references": ["Property X", "Jane Smith"],
        "ignored": "noop",
    }
    refs = extract_metadata_refs(metadata)
    assert refs == ["Alpha PE", "Property X", "Jane Smith"]


def test_build_date_version_format() -> None:
    stamp = datetime(2026, 4, 15, 12, 0, 0, tzinfo=timezone.utc)
    assert build_date_version(stamp) == "2026.04.15"


def test_build_release_writes_versioned_bundle(tmp_kb: Path, tmp_path: Path) -> None:
    defs_dir = tmp_path / "definitions"
    defs_dir.mkdir()
    (defs_dir / "actions.json").write_text(
        json.dumps(
            {
                "$schema_version": "2026.04.15",
                "action_types": {
                    "EnrichCompany": {
                        "action_id": "EnrichCompany",
                        "parameters": ["entity_id"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (defs_dir / "functions.json").write_text(
        json.dumps(
            {
                "$schema_version": "2026.04.15",
                "functions": {
                    "score_company": {
                        "function_id": "score_company",
                        "inputs": ["entity_id"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    config = BuilderConfig(
        kb_root=tmp_kb,
        ontology_id="chg_ontology",
        source_commit="abc123",
        version="2026.04.15",
    )
    builder = OntologyReleaseBuilder(config)

    bundle = builder.build_release(definitions_dir=defs_dir)
    out = write_release_bundle(bundle, tmp_path / "releases")

    assert out.exists()
    assert (out / "ontology.json").exists()
    assert (out / "objects.json").exists()
    assert (out / "links.json").exists()
    assert (out / "manifest.json").exists()

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["ontology_id"] == "chg_ontology"
    assert manifest["version"] == "2026.04.15"
    assert manifest["source_commit"] == "abc123"
    assert manifest["action_registry_version"] == "2026.04.15"
    assert manifest["function_registry_version"] == "2026.04.15"
    assert "ontology.json" in manifest["artifact_checksums"]

    ontology = json.loads((out / "ontology.json").read_text(encoding="utf-8"))
    assert ontology["ontology_id"] == "chg_ontology"
    assert ontology["version"] == "2026.04.15"
    assert "company" in ontology["object_types"]
    assert "action_types" in ontology
    assert "functions" in ontology


def test_build_release_handles_yaml_date_without_definitions(tmp_kb: Path, tmp_path: Path) -> None:
    dated_property = tmp_kb / "properties" / "property-dated.md"
    dated_property.write_text(
        """---
name: Property Dated
status: active
client: Alpha PE
closing_date: 2026-04-15
---
Date-bearing metadata for regression coverage.
""",
        encoding="utf-8",
    )

    config = BuilderConfig(
        kb_root=tmp_kb,
        ontology_id="chg_ontology",
        source_commit="abc123",
        version="2026.04.15",
    )
    builder = OntologyReleaseBuilder(config)

    bundle = builder.build_release(definitions_dir=None)
    out = write_release_bundle(bundle, tmp_path / "releases")

    objects = json.loads((out / "objects.json").read_text(encoding="utf-8"))
    dated_object = next(item for item in objects if item["entity_id"] == "property:property-dated")
    assert dated_object["properties"]["closing_date"] == "2026-04-15"

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert "objects.json" in manifest["artifact_checksums"]
