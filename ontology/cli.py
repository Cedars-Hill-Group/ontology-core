"""Command-line entry point for ontology-core.

Run with::

    python -m ontology.cli

or, after installing the package::

    ontology-collect

The command reads ``config.yaml``, walks the knowledge base, collects unique
``firm_type`` and ``focus`` values, and writes ``properties.json`` to the
configured output directory.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Collect property values and write ``properties.json``."""
    try:
        from ontology.config import get_knowledge_base_path, get_output_path, load_config
        from ontology.properties.collector import PropertyCollector
    except ImportError as exc:
        print(f"Import error: {exc}", file=sys.stderr)
        return 1

    try:
        config = load_config()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        kb_path = get_knowledge_base_path(config)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_dir = get_output_path(config)

    # Respect optional subdirectory overrides from config
    kb_cfg = config.get("knowledge_base", {})
    entity_dirs: dict[str, type] = {}
    if kb_cfg:
        from ontology.entities.company import Company
        from ontology.entities.person import Person
        from ontology.entities.project import Project

        entity_dirs = {
            kb_cfg.get("companies_dir", "companies"): Company,
            kb_cfg.get("people_dir", "people"): Person,
            kb_cfg.get("projects_dir", "projects"): Project,
        }

    collector = PropertyCollector(kb_path, entity_dirs=entity_dirs or None)
    catalog = collector.collect()

    output_path = output_dir / "properties.json"
    saved = catalog.save(output_path)
    print(f"Written: {saved}")
    print(
        f"  firm_type values : {len(catalog.firm_type)}\n"
        f"  focus values     : {len(catalog.focus)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
