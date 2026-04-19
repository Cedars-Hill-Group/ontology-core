"""Data models for ontology release builds."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EntityRecord:
    """Canonical entity record parsed from markdown knowledge files."""

    entity_id: str
    entity_type: str
    name: str
    source_path: str
    properties: dict[str, Any] = field(default_factory=dict)
    content: str = ""


@dataclass
class LinkRecord:
    """A directional link extracted from markdown or metadata references."""

    source_id: str
    source_path: str
    target_ref: str
    link_type: str


@dataclass
class ReleaseManifest:
    """Immutable release metadata for an ontology build artifact set."""

    ontology_id: str
    version: str
    source_commit: str
    build_time_utc: str
    schema_hash: str
    catalog_versions: dict[str, str]
    action_registry_version: str
    function_registry_version: str
    artifact_checksums: dict[str, str]


@dataclass
class ReleaseBundle:
    """All generated artifacts for a single ontology release."""

    ontology: dict[str, Any]
    objects: list[dict[str, Any]]
    links: list[dict[str, Any]]
    manifest: ReleaseManifest

    def to_files(self) -> dict[str, dict[str, Any] | list[dict[str, Any]]]:
        """Return a filename-to-content mapping for serialization."""
        return {
            "ontology.json": self.ontology,
            "objects.json": self.objects,
            "links.json": self.links,
            "manifest.json": {
                "ontology_id": self.manifest.ontology_id,
                "version": self.manifest.version,
                "source_commit": self.manifest.source_commit,
                "build_time_utc": self.manifest.build_time_utc,
                "schema_hash": self.manifest.schema_hash,
                "catalog_versions": self.manifest.catalog_versions,
                "action_registry_version": self.manifest.action_registry_version,
                "function_registry_version": self.manifest.function_registry_version,
                "artifact_checksums": self.manifest.artifact_checksums,
            },
        }


@dataclass
class BuilderConfig:
    """Runtime configuration for the ontology release builder."""

    kb_root: Path
    ontology_id: str = "knowledge_base"
    source_commit: str = "unknown"
    version: str | None = None
    entity_dirs: dict[str, str] = field(
        default_factory=lambda: {
            "company": "companies",
            "person": "people",
            "property": "properties",
        }
    )
