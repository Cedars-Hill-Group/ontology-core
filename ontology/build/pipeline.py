"""Release builder pipeline for ontology artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.property import Property
from ontology.registry import get_catalog_version

from ontology.build.link_extractor import extract_markdown_links, extract_metadata_refs
from ontology.build.models import BuilderConfig, EntityRecord, LinkRecord, ReleaseBundle, ReleaseManifest
from ontology.build.registry_loader import UserDefinitionRegistry


_ENTITY_CLASS_BY_TYPE = {
    "company": Company,
    "person": Person,
    "property": Property,
}


def build_date_version(now: datetime | None = None) -> str:
    """Return date-based ontology version in YYYY.MM.DD format."""
    stamp = now or datetime.now(timezone.utc)
    return stamp.strftime("%Y.%m.%d")


def _to_json_compatible(value: Any) -> Any:
    """Recursively convert values to JSON-serializable primitives."""
    if isinstance(value, dict):
        return {str(key): _to_json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_json_compatible(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return value


class OntologyReleaseBuilder:
    """Build release artifacts from markdown entities and user registries."""

    def __init__(self, config: BuilderConfig) -> None:
        self.config = config

    def _collect_entities(self) -> list[EntityRecord]:
        records: list[EntityRecord] = []
        for entity_type, rel_dir in self.config.entity_dirs.items():
            entity_dir = self.config.kb_root / rel_dir
            entity_class = _ENTITY_CLASS_BY_TYPE[entity_type]
            for entity in entity_class.iter_directory(entity_dir):
                entity_id = f"{entity_type}:{entity.path.stem}"
                if hasattr(entity, "to_dict"):
                    properties = dict(getattr(entity, "to_dict")())
                else:
                    properties = dict(entity.metadata)
                records.append(
                    EntityRecord(
                        entity_id=entity_id,
                        entity_type=entity_type,
                        name=entity.name,
                        source_path=str(entity.path),
                        properties=properties,
                        content=entity.content,
                    )
                )
        return records

    def _collect_links(self, entities: list[EntityRecord]) -> list[LinkRecord]:
        links: list[LinkRecord] = []
        for entity in entities:
            for target in extract_markdown_links(entity.content):
                links.append(
                    LinkRecord(
                        source_id=entity.entity_id,
                        source_path=entity.source_path,
                        target_ref=target,
                        link_type="markdown_link",
                    )
                )
            for target in extract_metadata_refs(entity.properties):
                links.append(
                    LinkRecord(
                        source_id=entity.entity_id,
                        source_path=entity.source_path,
                        target_ref=target,
                        link_type="metadata_ref",
                    )
                )
        return links

    def _synthesize_schema(self, entities: list[EntityRecord]) -> dict[str, Any]:
        schema: dict[str, dict[str, Any]] = {}
        for entity in entities:
            entry = schema.setdefault(
                entity.entity_type,
                {
                    "type_id": entity.entity_type,
                    "display_name": entity.entity_type.title(),
                    "primary_key": "entity_id",
                    "properties": {"entity_id", "name"},
                },
            )
            entry["properties"].update(entity.properties.keys())

        object_types = {}
        for key, value in schema.items():
            object_types[key] = {
                "type_id": value["type_id"],
                "display_name": value["display_name"],
                "primary_key": value["primary_key"],
                "properties": sorted(value["properties"]),
            }
        return object_types

    def build_release(self, definitions_dir: str | Path | None = None) -> ReleaseBundle:
        """Build a release bundle from configured sources."""
        version = self.config.version or build_date_version()
        entities = self._collect_entities()
        links = self._collect_links(entities)
        object_types = self._synthesize_schema(entities)

        actions: dict[str, Any] = {}
        functions: dict[str, Any] = {}
        action_version = "unknown"
        function_version = "unknown"
        if definitions_dir is not None:
            registry = UserDefinitionRegistry(definitions_dir)
            actions = registry.load_actions()
            functions = registry.load_functions()
            action_version = str(actions.get("$schema_version", "unknown"))
            function_version = str(functions.get("$schema_version", "unknown"))

        ontology = {
            "ontology_id": self.config.ontology_id,
            "version": version,
            "object_types": object_types,
            "link_types": {
                "markdown_link": {
                    "link_id": "markdown_link",
                    "source_type": "*",
                    "target_type": "*",
                },
                "metadata_ref": {
                    "link_id": "metadata_ref",
                    "source_type": "*",
                    "target_type": "*",
                },
            },
            "action_types": actions.get("action_types", {}),
            "functions": functions.get("functions", {}),
        }

        objects = []
        for entity in entities:
            objects.append(
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "name": entity.name,
                    "source_path": entity.source_path,
                    "properties": entity.properties,
                }
            )

        link_rows = [asdict(link) for link in links]

        ontology = _to_json_compatible(ontology)
        objects = _to_json_compatible(objects)
        link_rows = _to_json_compatible(link_rows)

        serialized = {
            "ontology.json": ontology,
            "objects.json": objects,
            "links.json": link_rows,
        }
        artifact_checksums = {
            name: hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            for name, payload in serialized.items()
        }

        schema_hash = hashlib.sha256(
            json.dumps(object_types, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        manifest = ReleaseManifest(
            ontology_id=self.config.ontology_id,
            version=version,
            source_commit=self.config.source_commit,
            build_time_utc=datetime.now(timezone.utc).isoformat(),
            schema_hash=schema_hash,
            catalog_versions={
                "attributes": get_catalog_version("attributes"),
                "naics": get_catalog_version("naics"),
                "activity_cycle": get_catalog_version("activity_cycle"),
            },
            action_registry_version=action_version,
            function_registry_version=function_version,
            artifact_checksums=artifact_checksums,
        )

        return ReleaseBundle(
            ontology=ontology,
            objects=objects,
            links=link_rows,
            manifest=manifest,
        )


def write_release_bundle(bundle: ReleaseBundle, output_dir: str | Path) -> Path:
    """Write release artifacts to `output_dir/<ontology_id>/<version>/`."""
    root = Path(output_dir) / bundle.manifest.ontology_id / bundle.manifest.version
    root.mkdir(parents=True, exist_ok=True)

    for file_name, data in bundle.to_files().items():
        target = root / file_name
        payload = _to_json_compatible(data)
        target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return root
