## ontology-core

Central library for canonical ontology entities, catalogs, and release-build artifacts used by CHG knowledge systems.

---

## What Is New

This repository now includes a release builder that can:

1. Read markdown knowledge-base entities (`companies`, `people`, `properties`).
2. Extract links from markdown bodies and metadata references.
3. Synthesize object types for an ontology payload.
4. Merge user-defined actions/functions from external JSON registries.
5. Emit a date-versioned release bundle with checksummed artifacts.

This is the first implementation slice for the larger flow:
markdown knowledge base -> versioned ontology bundle -> GCS publish -> graph load (Node.js) -> MCP exposure.

---

## Project Structure

```text
ontology-core/
├── ontology/
│   ├── entities/                # Markdown entity adapters
│   ├── catalogs/                # Canonical catalogs
│   ├── registry/                # Catalog registry APIs
│   └── build/                   # New release builder pipeline
│       ├── __init__.py
│       ├── models.py
│       ├── link_extractor.py
│       ├── registry_loader.py
│       └── pipeline.py
├── schemas/
├── docs/
└── tests/
    ├── test_entities.py
    └── test_build.py
```

---

## Installation

### Development

```bash
pip install -e ".[dev]"
```

### Production

```bash
pip install -e .
```

Python 3.10+ is required.

---

## Quickstart (Copy/Paste)

Use this minimal example to generate a release bundle in one run.

### 1) Create a sample knowledge base

```text
tmp-kb/
  companies/
    alpha-pe.md
  people/
    jane-smith.md
  properties/
    property-x.md
  definitions/
    actions.json
    functions.json
```

`tmp-kb/companies/alpha-pe.md`:

```md
---
name: Alpha PE
firm_type: private_equity
focus: [technology, healthcare]
website: https://alphape.example.com
---
See [Property X](../properties/property-x.md)
```

`tmp-kb/people/jane-smith.md`:

```md
---
name: Jane Smith
title: Managing Director
company: Alpha PE
email: jane@alphape.example.com
---
Primary sponsor for [Alpha PE](../companies/alpha-pe.md)
```

`tmp-kb/properties/property-x.md`:

```md
---
name: Property X
status: active
client: Alpha PE
---
Healthcare asset mandate.
```

`tmp-kb/definitions/actions.json`:

```json
{
  "$schema_version": "2026.04.15",
  "action_types": {
    "EnrichCompany": {
      "action_id": "EnrichCompany",
      "parameters": ["entity_id"]
    }
  }
}
```

`tmp-kb/definitions/functions.json`:

```json
{
  "$schema_version": "2026.04.15",
  "functions": {
    "score_company": {
      "function_id": "score_company",
      "inputs": ["entity_id"]
    }
  }
}
```

### 2) Run the builder

```python
from pathlib import Path

from ontology.build import BuilderConfig, OntologyReleaseBuilder, write_release_bundle

config = BuilderConfig(
    kb_root=Path("tmp-kb"),
    ontology_id="demo_ontology",
    source_commit="local-dev",
)

builder = OntologyReleaseBuilder(config)
bundle = builder.build_release(definitions_dir=Path("tmp-kb/definitions"))
release_path = write_release_bundle(bundle, Path("releases"))
print(f"Release written to: {release_path}")
```

### 3) Verify artifacts

```text
releases/demo_ontology/<YYYY.MM.DD>/
  ontology.json
  objects.json
  links.json
  manifest.json
```

---

## Existing Usage

### Catalog API

```python
from ontology.registry import get_catalog, list_catalogs

print(list_catalogs())
attributes = get_catalog("attributes")
```

### Entity Parsing

```python
from ontology.entities.company import Company

companies = Company.iter_directory("/path/to/kb/companies")
for company in companies:
    print(company.name, company.firm_type, company.focus)
```

---

## New Usage: Build a Versioned Ontology Release Bundle

The builder API is exposed from `ontology.build`.

### 1) Prepare your knowledge base layout

The root knowledge-base directory should include:

```text
/path/to/kb/
  companies/*.md
  people/*.md
  properties/*.md
```

### 2) Optional user definition registries

Create a directory containing:

- `actions.json`
- `functions.json`

Each file must include `$schema_version`.

Example `actions.json`:

```json
{
  "$schema_version": "2026.04.15",
  "action_types": {
    "EnrichCompany": {
      "action_id": "EnrichCompany",
      "parameters": ["entity_id"]
    }
  }
}
```

Example `functions.json`:

```json
{
  "$schema_version": "2026.04.15",
  "functions": {
    "score_company": {
      "function_id": "score_company",
      "inputs": ["entity_id"]
    }
  }
}
```

### 3) Build and write a release

```python
from pathlib import Path

from ontology.build import BuilderConfig, OntologyReleaseBuilder, write_release_bundle

config = BuilderConfig(
    kb_root=Path("/path/to/kb"),
    ontology_id="chg_ontology",
    source_commit="abc123",      # git SHA or release reference
    version="2026.04.15",        # optional; defaults to YYYY.MM.DD in UTC
)

builder = OntologyReleaseBuilder(config)
bundle = builder.build_release(definitions_dir=Path("/path/to/definitions"))

release_path = write_release_bundle(bundle, Path("./releases"))
print(release_path)
```

If `version` is omitted, the builder uses date-based versioning in `YYYY.MM.DD` format.

### 4) Output artifact layout

The writer creates:

```text
<output_dir>/<ontology_id>/<version>/
  ontology.json
  objects.json
  links.json
  manifest.json
```

### 5) What each artifact contains

- `ontology.json`: synthesized object types, default link types, and optional actions/functions.
- `objects.json`: normalized object snapshot derived from markdown entities.
- `links.json`: extracted markdown/body and metadata links.
- `manifest.json`: immutable release metadata including checksums, schema hash, catalog versions, and registry versions.

---

## Current Scope and Next Steps

Implemented now:

1. Deterministic bundle generation and local artifact writing.
2. Date-versioned releases and content checksums.
3. User-defined action/function registry loading.

Planned next:

1. GCS publishing flow (staging + checksum verification + latest pointer).
2. Node.js graph loader for Neo4j.
3. Release CLI/workflow wiring.

---

## Testing

```bash
pytest -q
```

`tests/test_build.py` covers the new release-builder behavior.


---
