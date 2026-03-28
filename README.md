*# ontology-core

Central library of the canonical object models for the CHG Operating System.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Key Concepts](#key-concepts)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI](#cli)
  - [Python API](#python-api)
- [Workflow](#workflow)
- [Importing into Other Projects](#importing-into-other-projects)

---

## Project Structure

```
ontology-core/
├── ontology/                    # Main Python package
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point (ontology-collect command)
│   ├── config.py                # Config loader (config.yaml → Python dict)
│   ├── entities/                # Entity object models
│   │   ├── __init__.py
│   │   ├── base.py              # OntologyEntity base class
│   │   ├── company.py           # Company entity
│   │   ├── person.py            # Person entity
│   │   ├── property.py          # Property entity
│   │   └── utils.py             # Shared helpers (e.g. as_list)
│   ├── properties/              # Property value layer
│   │    ├── __init__.py
│   │    ├── collector.py        # PropertyCollector — walks KB and collects values
│   │    └── models.py           # Pydantic models: PropertyValue, PropertyCatalog
│   │ 
│   └── objects/                 # Ontology object models (documents, PDFs, emails, etc.)
│
├── schemas/                     # Markdown front-matter templates
│   ├── general/                 # Generic entity templates
│   │   ├── template.md
│   │   ├── extraction.md
│   │   └── output.md
│   └── commercial_real_estate/  # CRE-specific templates (extra front-matter fields)
│       ├── template.md
│       ├── extraction.md
│       └── output.md
├── tests/                       # pytest test suite
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_entities.py
│   └── test_properties.py
├── config.yaml.example          # Configuration template — copy to config.yaml
├── pyproject.toml               # Package metadata and tool configuration
└── README.md
```

---

## Key Concepts

### Entities

Every entity in the knowledge base is a Markdown file whose **YAML front matter** contains structured metadata and whose body contains free-form prose.

| Class | `entity_type` | Key front-matter fields |
|-------|--------------|-------------------------|
| `Company` | `company` | `name`, `firm_type`, `focus`, `website`, `city`, `state` |
| `Person` | `person` | `name`, `focus`, `company`, `emails`, `phones`, `linkedin` |
| `Property` | `property` | `name`, `address`, `city`, `state`, `zip`, `prop_type` |

All three extend `OntologyEntity`, which provides:

- `name` — human-readable name from front matter, falling back to the filename stem.
- `metadata` — all front-matter fields as a plain `dict`.
- `content` — the Markdown body text.
- `get(key, default)` — type-safe accessor for individual front-matter values.
- `iter_directory(path)` — class method that loads every `.md` file in a directory and returns a sorted list of entity instances.

### PropertyValue and PropertyCatalog

`PropertyValue` pairs a normalised snake_case identifier with a human-readable description:

```json
{
  "value": "private_equity",
  "description": "A private equity firm that invests in private companies ..."
}
```

`PropertyCatalog` is the top-level JSON output that groups allowed values for `firm_type` and `focus`:

```json
{
  "firm_type": [ { "value": "...", "description": "..." }, ... ],
  "focus":     [ { "value": "...", "description": "..." }, ... ]
}
```

### PropertyCollector

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

## Configuration

The CLI and config loader expect a `config.yaml` file at the repository root.  This file is **git-ignored** to protect local paths.

1. Copy the example file:

   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit `config.yaml` and set the paths for your environment:

   ```yaml
   knowledge_base:
     path: "/absolute/path/to/your/knowledge-base"

     # Optional — override only if your directory names differ from the defaults
     companies_dir: "companies"   # default
     people_dir: "people"         # default
    properties_dir: "properties" # default

   output:
     path: "output"   # relative or absolute; created automatically if absent
   ```

The knowledge base directory is expected to contain subdirectories named `companies/`, `people/`, and `properties/` (or whatever names you configure), each holding `.md` files with YAML front matter.

---

## Usage

### CLI

After installing the package the `ontology-collect` command is available on your `PATH`:

```bash
ontology-collect
```

Alternatively, run the module directly without installing:

```bash
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
```

#### Collecting property values programmatically

```python
from ontology.properties.collector import PropertyCollector

collector = PropertyCollector("/path/to/knowledge-base")
catalog   = collector.collect()

# Inspect values
for pv in catalog.firm_type:
    print(pv.value, "—", pv.description)

# Save to JSON
catalog.save("output/properties.json")
```

#### Loading a saved catalog

```python
from ontology.properties.models import PropertyCatalog

catalog = PropertyCatalog.load("output/properties.json")
print(catalog.firm_type)
print(catalog.focus)
```

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
3. **`PropertyCollector`** walks the knowledge base, gathers every unique `firm_type` and `focus` value, normalises it to snake_case, and pairs it with a human-readable description.
4. **`PropertyCatalog`** is serialised to `properties.json` and consumed by downstream systems (data ingestion pipelines, LLM classification prompts, domain services, etc.).

---

## Importing into Other Projects

`ontology-core` is a standard Python package and can be consumed as a library dependency.

### Install directly from GitHub

```bash
pip install git+https://github.com/rounder22/ontology-core.git
```

Pin to a specific tag or commit for reproducible builds:

```bash
pip install git+https://github.com/rounder22/ontology-core.git@v0.1.0
pip install git+https://github.com/rounder22/ontology-core.git@<commit-sha>
```

### Add to `pyproject.toml`

```toml
[project]
dependencies = [
    "ontology-core @ git+https://github.com/rounder22/ontology-core.git@v0.1.0",
]
```

### Add to `requirements.txt`

```
ontology-core @ git+https://github.com/rounder22/ontology-core.git@v0.1.0
```

### Example usage in a downstream project

```python
from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.properties.collector import PropertyCollector
from ontology.properties.models import PropertyCatalog

# Load entities
companies = Company.iter_directory("/path/to/kb/companies")

# Load a pre-built catalog (no knowledge base required)
catalog = PropertyCatalog.load("/path/to/properties.json")
allowed_firm_types = [pv.value for pv in catalog.firm_type]

# Or collect fresh from a knowledge base
collector = PropertyCollector("/path/to/knowledge-base")
catalog   = collector.collect()
```

### Runtime dependencies

When installed as a library the following packages are required (declared in `pyproject.toml` and installed automatically):

| Package | Purpose |
|---------|---------|
| `python-frontmatter>=1.1.0` | Parse YAML front matter from Markdown files |
| `pydantic>=2.0` | Data validation and JSON serialisation for `PropertyCatalog` |
| `pyyaml>=6.0` | YAML config file parsing |

Python **3.10 or newer** is required.

