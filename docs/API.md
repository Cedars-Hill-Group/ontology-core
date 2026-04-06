# Ontology Registry API Reference

The `ontology.registry` module provides a stable, versioned API for accessing canonical ontology catalogs.

---

## Overview

The registry is the authoritative source for ontology data in downstream applications. It exposes three core functions:

- **`get_catalog(name, version=None)`** — load a catalog by name
- **`list_catalogs()`** — enumerate available catalogs
- **`get_catalog_version(name)`** — get the schema version of a catalog

All functions are thread-safe and use in-memory caching for performance.

---

## API Reference

### `get_catalog(name: str, version: str | None = None) -> dict[str, Any]`

Load a catalog by name.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | (required) | Catalog identifier: `"attributes"`, `"naics"`, or `"activity_cycle"` |
| `version` | `str \| None` | `None` | Ontology version. Reserved for future use. Currently ignored. |

**Returns:**

A dictionary containing:
- `$ontology_id` (str): Catalog identifier
- `$schema_version` (str): SemVer version of the catalog
- Catalog-specific fields (see [Catalog Formats](#catalog-formats) below)

**Raises:**

- `FileNotFoundError` — if the catalog does not exist

**Examples:**

```python
from ontology.registry import get_catalog

# Load attributes catalog
attributes = get_catalog("attributes")
print(attributes["$ontology_id"])       # "attributes"
print(attributes["$schema_version"])    # "1.0.0"

# Access firm_type values
for entry in attributes["firm_type"]:
    print(f"{entry['value']}: {entry['description']}")
    # Output:
    # private_equity: A private equity firm that invests in private companies...
    # family_office: A private wealth management entity...
```

---

### `list_catalogs() -> list[str]`

Enumerate all available catalogs.

**Returns:**

A list of catalog names:

```python
["attributes", "naics", "activity_cycle"]
```

**Examples:**

```python
from ontology.registry import list_catalogs

catalogs = list_catalogs()
for name in catalogs:
    print(name)
```

---

### `get_catalog_version(name: str) -> str`

Get the schema version of a catalog.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | Catalog name |

**Returns:**

SemVer version string (e.g., `"1.0.0"`)

**Raises:**

- `FileNotFoundError` — if the catalog does not exist

**Examples:**

```python
from ontology.registry import get_catalog_version

version = get_catalog_version("attributes")  # "1.0.0"
naics_version = get_catalog_version("naics")  # "1.0.0"

# Check if a catalog is new enough
from packaging import version as pkg_version
min_version = "1.0.0"
if pkg_version.parse(version) < pkg_version.parse(min_version):
    raise RuntimeError(f"Catalog version {version} is too old")
```

---

## Catalog Formats

### Attributes Catalog

**Name:** `"attributes"`  
**$ontology_id:** `"attributes"`  
**$schema_version:** `"1.0.0"`

Contains classifications for firm type and focus/industry.

**Structure:**

```python
{
  "$ontology_id": "attributes",
  "$schema_version": "1.0.0",
  "firm_type": [
    {
      "value": "private_equity",
      "description": "A private equity firm that invests in private companies..."
    },
    {
      "value": "hedge_fund",
      "description": "An actively managed investment fund..."
    },
    # ... more entries
  ],
  "focus": [
    {
      "value": "commercial_real_estate",
      "description": "Investment, development, or operation of income-producing..."
    },
    {
      "value": "technology",
      "description": "Software, hardware, semiconductors, and technology-enabled..."
    },
    # ... more entries
  ]
}
```

**Usage:**

```python
from ontology.registry import get_catalog

attrs = get_catalog("attributes")

# Build a lookup map
firm_types = {e["value"]: e["description"] for e in attrs["firm_type"]}
focuses = {e["value"]: e["description"] for e in attrs["focus"]}

# Validate a value
if my_firm_type not in firm_types:
    raise ValueError(f"Unknown firm_type: {my_firm_type}")
```

---

### NAICS Catalog

**Name:** `"naics"`  
**$ontology_id:** `"naics"`  
**$schema_version:** `"1.0.0"`

Contains North American Industry Classification System (NAICS) sector classifications.

**Structure:**

```python
{
  "$ontology_id": "naics",
  "$schema_version": "1.0.0",
  "naics_sectors": [
    {
      "code": "11",
      "title": "Agriculture, Forestry, Fishing and Hunting",
      "description": "Industries engaged in growing crops, raising animals..."
    },
    {
      "code": "21",
      "title": "Mining, Quarrying, and Oil and Gas Extraction",
      "description": "Industries that extract naturally occurring minerals..."
    },
    # ... more sectors
  ]
}
```

**Usage:**

```python
from ontology.registry import get_catalog

naics = get_catalog("naics")

# Build code → sector map
sectors_by_code = {e["code"]: e for e in naics["naics_sectors"]}

# Look up a sector
sector_22 = sectors_by_code["22"]
print(sector_22["title"])  # "Utilities"
```

---

### Activity Cycle Catalog

**Name:** `"activity_cycle"`  
**$ontology_id:** `"activity_cycle"`  
**$schema_version:** `"1.0.0"`

Hierarchical taxonomy of business activities and processes.

**Structure:**

```python
{
  "$ontology_id": "activity_cycle",
  "$schema_version": "1.0.0",
  "ActivityCycle": [
    {
      "ActivityID": "1.1.1",
      "Phase": "1 Procures",
      "Part": "1.1 Sources",
      "Section": "1.1.1",
      "FormalDefinition": "Collects and synthesizes all information...",
      "Colloquial": "Researches potential purchases",
      "Examples": "Procurement Consulting, Supply Chain Research",
      "IO": "C2i, C2ii, C2iii, C3ii, C3iii"
    },
    {
      "ActivityID": "1.1.2",
      "Phase": "1 Procures",
      "Part": "1.1 Sources",
      "Section": "1.1.2",
      "FormalDefinition": "Negotiates price with suppliers...",
      "Colloquial": "Buys resources",
      "Examples": "Buy-side Broker, Auction Houses, Employee Recruitment",
      "IO": "C4ii"
    },
    # ... more activities
  ]
}
```

**Usage:**

```python
from ontology.registry import get_catalog

activity = get_catalog("activity_cycle")

# Build ActivityID → entry map
activities_by_id = {
    e["ActivityID"]: e for e in activity["ActivityCycle"]
}

# Look up an activity
activity_111 = activities_by_id["1.1.1"]
print(activity_111["Colloquial"])  # "Researches potential purchases"
```

---

## Versioning

### Catalog Versioning Strategy

Each catalog carries a `$schema_version` in SemVer format: `MAJOR.MINOR.PATCH`

| Version | Change Type | Backward Compatible | When to Upgrade |
|---------|-------------|---------------------|-----------------|
| **Patch** (0.0.X) | Descriptions only | ✅ Yes | Anytime |
| **Minor** (0.X.0) | New values added | ✅ Yes | When you need new values |
| **Major** (X.0.0) | Values removed/renamed | ❌ No | Requires code review |

### Two-Layer Versioning

The ontology-core package uses two independent versions:

| Layer | File | Purpose | Bump When |
|-------|------|---------|-----------|
| **Package** | `pyproject.toml` | Python code/API changes | Refactoring, new features, bug fixes |
| **Ontology** | `ontology/registry/version.py` | Catalog format/content changes | Any catalog is updated |

Example: Package `v0.2.0` with Ontology `1.0.0` means:
- Code API is at version 0.2.0
- Catalog schemas are at version 1.0.0 (independent of code)

### Checking Compatibility

```python
from ontology.registry import get_catalog_version
from packaging import version as pkg_version

# Assert minimum catalog version
min_required = "1.0.0"
actual = get_catalog_version("attributes")

if pkg_version.parse(actual) < pkg_version.parse(min_required):
    raise RuntimeError(
        f"Catalogs too old: {actual} < {min_required}. "
        f"Upgrade ontology-core package."
    )
```

---

## Error Handling

### FileNotFoundError

Raised when a catalog name does not exist.

```python
from ontology.registry import get_catalog

try:
    bad_catalog = get_catalog("nonexistent")
except FileNotFoundError as e:
    print(f"Catalog not found: {e}")
    # Output: Catalog 'nonexistent' not found in ontology.catalogs
```

### Handling Missing Keys

Catalogs are dictionaries; access values safely:

```python
from ontology.registry import get_catalog

attrs = get_catalog("attributes")

# Safe access with get()
version = attrs.get("$schema_version", "unknown")

# Safe iteration
for entry in attrs.get("firm_type", []):
    print(entry["value"])
```

---

## Performance Considerations

### Caching

Catalogs are loaded and cached in memory on first access:

```python
# First call: loads from disk
attrs1 = get_catalog("attributes")

# Subsequent calls: returned from cache
attrs2 = get_catalog("attributes")
# attrs2 is the same object as attrs1
```

For testing, clear the cache:

```python
from ontology.registry import CatalogRegistry

CatalogRegistry.clear_cache()
```

### Thread Safety

All registry functions are thread-safe. Concurrent calls to `get_catalog()` are safe:

```python
from concurrent.futures import ThreadPoolExecutor
from ontology.registry import get_catalog

def load_catalog(name):
    return get_catalog(name)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(load_catalog, ["attributes", "naics"]))
# Safe for concurrent access
```

---

## Integration Patterns

### Pattern 1: Validate User Input

```python
from ontology.registry import get_catalog

def validate_firm_type(value: str) -> bool:
    """Check if a firm_type value is valid."""
    attrs = get_catalog("attributes")
    valid_values = {e["value"] for e in attrs["firm_type"]}
    return value in valid_values

if not validate_firm_type(user_input):
    raise ValueError(f"Invalid firm_type: {user_input}")
```

### Pattern 2: Build Enum or Constant Map

```python
from enum import Enum
from ontology.registry import get_catalog

class FirmType(str, Enum):
    """Auto-generated enum from catalog."""
    pass

attrs = get_catalog("attributes")
for entry in attrs["firm_type"]:
    setattr(FirmType, entry["value"].upper(), entry["value"])

# Now use as:
# FirmType.PRIVATE_EQUITY, FirmType.HEDGE_FUND, etc.
```

### Pattern 3: Generate Database Schema

```python
from ontology.registry import get_catalog
import sqlalchemy as sa

def create_firm_type_enum(engine):
    """Create a PostgreSQL ENUM type from catalog."""
    attrs = get_catalog("attributes")
    values = [e["value"] for e in attrs["firm_type"]]
    
    # For PostgreSQL
    enum_type = sa.Enum(*values, name="firm_type")
    enum_type.create(engine, checkfirst=True)
```

### Pattern 4: Document LLM Prompts

```python
from ontology.registry import get_catalog

def build_llm_prompt(user_query: str) -> str:
    """Build a prompt with catalog values for LLM classification."""
    attrs = get_catalog("attributes")
    
    firm_types_text = "\n".join([
        f"  - {e['value']}: {e['description']}"
        for e in attrs["firm_type"]
    ])
    
    prompt = f"""
You are classifying firms. Choose from these firm_type values:

{firm_types_text}

User input: {user_query}

Respond with the firm_type value only.
"""
    return prompt
```

---

## Migration Guide

### From PropertyCatalog (Legacy)

If your code previously used `PropertyCatalog` from `ontology.properties.models`:

**Before (removed):**
```python
from ontology.properties.models import PropertyCatalog
catalog = PropertyCatalog.load("path/to/properties.json")
for pv in catalog.firm_type:
    print(pv.value)
```

**After:**
```python
from ontology.registry import get_catalog
catalog = get_catalog("attributes")
for entry in catalog["firm_type"]:
    print(entry["value"])
```

Key differences:
- `get_catalog()` loads from package data, not from a file path
- Catalog entries are plain dicts, not Pydantic models
- Access fields directly: `entry["value"]` instead of `entry.value`

---

## Support & Versioning Policy

### Stability Guarantee

The registry API (`get_catalog`, `list_catalogs`, `get_catalog_version`) is stable and will not change in incompatible ways without a major version bump to the package.

### Catalog Evolution

Catalogs are independently versioned. Your code should:
1. Call `get_catalog_version()` to check the catalog version
2. Assert minimum required versions in your startup code
3. Handle missing values gracefully (use `.get()` and safe iteration)

### Deprecation Notice

The `PropertyCollector` and `PropertyCatalog` classes were removed in v0.2.0. Use `get_catalog("attributes")` instead.

