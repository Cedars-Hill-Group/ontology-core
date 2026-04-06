*# ontology-core

Central library of the canonical object models for the CHG Operating System.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Key Concepts](#key-concepts)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Usage](#usage)
  - [Accessing Catalogs](#accessing-catalogs)
  - [Working with Entities](#working-with-entities)
- [Architecture](#architecture)
- [Importing into Other Projects](#importing-into-other-projects)

---

## Project Structure

```
ontology-core/
├── ontology/                    # Main Python package
│   ├── __init__.py
│   ├── entities/                # Entity object models
│   │   ├── __init__.py
│   │   ├── base.py              # OntologyEntity base class
│   │   ├── company.py           # Company entity
│   │   ├── person.py            # Person entity
│   │   ├── property.py          # Property entity
│   │   └── utils.py             # Shared helpers (e.g. as_list)
│   ├── catalogs/                # Canonical ontology catalogs (JSON)
│   │   ├── attributes.json      # firm_type and focus classifications
│   │   ├── naics.json           # NAICS sector classification
│   │   └── activity_cycle.json  # Activity/process classifications
│   ├── registry/                # Ontology catalog registry and API
│   │   ├── __init__.py          # Public API: get_catalog, list_catalogs, get_catalog_version
│   │   ├── catalog.py           # CatalogRegistry class
│   │   ├── loader.py            # importlib-based catalog loader
│   │   └── version.py           # Ontology versioning
│   │ 
│   └── core/                    # [Phase 2+] Formal ontology type system
│
├── docs/                        # Comprehensive documentation
│   ├── API.md                   # Complete API reference
│   ├── INTEGRATION.md           # Integration guide for downstream apps
│   ├── CATALOG_FORMAT.md        # Formal catalog specifications
│   └── README.md                # Documentation index
├── schemas/                     # Markdown front-matter templates
│   ├── general/                 # Generic entity templates
│   │   ├── template.md
│   │   ├── extraction.md
│   │   └── output.md
│   └── commercial_real_estate/  # CRE-specific templates
│       ├── template.md
│       ├── extraction.md
│       └── output.md
├── tests/                       # pytest test suite
│   ├── conftest.py
│   ├── test_entities.py
│   └── test_registry.py
├── pyproject.toml               # Package metadata and tool configuration
└── README.md
```

---

## Key Concepts
Catalogs

Ontology catalogs are canonical, versioned JSON files that define allowed values and classifications:

| Catalog | Purpose | Content |
|---------|---------|---------|
| `attributes` | Firm and focus classifications | `firm_type` and `focus` values with descriptions |
| `naics` | Industry classification | NAICS sector codes and titles |
| `activity_cycle` | Process/activity taxonomy | Hierarchical activity classifications |

Each catalog carries metadata:
- `$ontology_id`: unique identifier (e.g., `"attributes"`)
- `$schema_version`: SemVer version (e.g., `"1.0.0"`)

Catalogs are first-class ontology assets shipped as part of the package and accessible via the registry API.

### Entities

Entity classes (Company, Person, Property) represent instances of real-world objects. They optionally integrate with knowledge base Markdown files via the `OntologyEntity` base class, which provides:

- `name` — human-readable name from front matter or filename.
- `metadata` — all front-matter fields as a plain `dict`.
- `content` — Markdown body text.
- `get(key, default)` — accessor for individual front-matter values.
- `iter_directory(path)` — load all `.md` files from a directory
`PropertyCollector` walks the knowledge base, reads every entity file, normalises the `firm_type` and `focus` values (lowercased, whitespace/hyphens collapsed to underscores), and assembles a `PropertyCatalog`.  Built-in description tables enrich common values; newly discovered values receive an auto-generated placeholder description.

---

## Installation

### Development / local

```bash
# From the repository root
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `pytest-cov`, and `ruff`.

### Production (no dev tools)

```bash
pip install -e .
```

---


```bash
# From the repository root
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `pytest-cov`, and `ruff`.

### Production

```bash
pip install -e .
```

### From GitHub

Pin to a specific version:

```bash
pip install git+https://github.com/rounder22/ontology-core.git@v0.2.0
```

Or add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "ontology-core @ git+https://github.com/rounder22/ontology-core.git@v0.2.0",
]
```
python -m ontology.cli
```

Both commands:

1. Read `config.yaml`.
2. Walk the knowledge base and collect all unique `firm_type` and `focus` values.
3. Write a normalised `properties.json` to the configured output directory.
4. Print a summary:

   ```
   Written: /path/to/output/properties.json
     firm_type values : 5
     focus values     : 8
   ```

### Python API
Accessing Catalogs

Load catalogs using the registry API:

```python
from ontology.registry import get_catalog, list_catalogs, get_catalog_version

# List all available catalogs
catalogs = list_catalogs()
print(catalogs)  # ["attributes", "naics", "activity_cycle"]

# Load a catalog
attributes = get_catalog("attributes")
Entity classes are optional and designed for applications that use Markdown knowledge bases. They integrate with catalogs but are not required for catalog access.

#### Loading entities from a directory

```python
from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.property import Property

companies = Company.iter_directory("/path/to/kb/companies")
people    = Person.iter_directory("/path/to/kb/people")
properties = Property.iter_directory("/path/to/kb/properties")

for company in companies:
    print(company.name, company.firm_type, company.focus)
```

#### Loading a single entity

```python
from ontology.entities.company import Company

company = Company("/path/to/kb/companies/acme-capital.md")
print(company.name)          # "Acme Capital"
print(company.firm_type)     # ["private_equity"]
print(company.focus)         # ["commercial_real_estate"]
print(company.metadata)      # full front-matter dict
print(company.content)       # Markdown body

---

## Workflow

```
Knowledge Base (Markdown files)
        │
        │  YAML front matter: name, firm_type, focus, ...
        ▼
  OntologyEntity subclasses
  (Company / Person / Property)
        │
        │  .iter_directory(path)
        ▼
  PropertyCollector.collect()
        │
        │  normalise → deduplicate → enrich with descriptions
        ▼
  PropertyCatalog  ──►  properties.json
        │
        │  consumed by downstream layers
        ▼
  Data pipelines / LLM prompts / domain services
```

1. **Markdown files** in the knowledge base carry structured metadata in YAML front matter.
2. **Entity classes** parse those files and expose typed accessors for each property.
3. Architecture

### Catalog-First Distribution

```
Canonical Catalogs (JSON)
  ├─ attributes.json
  ├─ naics.json
  └─ activity_cycle.json
       │
       │  Packaged as ontology/catalogs/*.json
       │  (included in installed wheel)
       ▼
  CatalogRegistry
       │
       │  importlib.resources loader
       │  in-memory caching
       ▼
  Public API: get_catalog(name, version=None)
       │
       ├─► Downstream Python applications
       ├─► LLM pipelines (enum values, descriptions)
       ├─► Database schema generators
       └─► Documentation tools
```

### Entities (Optional Markdown Adapter)

Entity classes are designed for applications that use knowledge bases with Markdown files:

```
Markdown Knowledge Base
  └─ companies/distributed as a wheel that includes catalogs as package data.

### Install from GitHub

Pin to a specific version:

```bash
pip install git+https://github.com/rounder22/ontology-core.git@v0.2.0
```

Or use in `pyproject.toml`:

```toml
[project]
dependencies = [
    "ontology-core @ git+https://github.com/rounder22/ontology-core.git@v0.2.0",
]
```

### Usage in Downstream Projects

**Minimal usage (catalogs only):**

```python
from ontology.registry import get_catalog, list_catalogs

# No knowledge base required — standalone catalog access
attributes = get_catalog("attributes")
firm_types = {entry["value"]: entry["description"] 
              for entry in attributes["firm_type"]}
```

**With entity parsing (requires knowledge base):**

```python
from ontology.entities.company import Company
from ontology.registry import get_catalog

# Load catalogs
attributes = get_catalog("attributes")

# Load entities from knowledge base
companies = Company.iter_directory("/path/to/kb/companies")
for company in companies:
    # Entity properties are validated against catalogs in Phase 2+
    print(company.name, company.firm_type, company.focus)
```

### Runtime Dependencies

Core library:

| Package | Purpose | When needed |
|---------|---------|-------------|
| (none) | Catalog access is pure Python | Always |
| `python-frontmatter>=1.1.0` | Parse Markdown entity files | Only if using entity classes |

Python **3.10 or newer** is required.

### Optional: Non-Python Consumers

For non-Python services, download catalogs from GitHub Releases as `ontology-artifacts-1.0.0.zip` (available starting in Phase 3)
### Runtime dependencies

When installed as a library the following packages are required (declared in `pyproject.toml` and installed automatically):

| Package | Purpose |
|---------|---------|
| `python-frontmatter>=1.1.0` | Parse YAML front matter from Markdown files |
| `pydantic>=2.0` | Data validation and JSON serialisation for `PropertyCatalog` |
| `pyyaml>=6.0` | YAML config file parsing |

Python **3.10 or newer** is required.

