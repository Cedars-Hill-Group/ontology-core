# Catalog Format Specification

This document defines the formal structure of all ontology catalogs.

---

## Overview

All catalogs are JSON files stored in `ontology/catalogs/` and distributed as part of the package data. Each catalog is a JSON object with specific structure.

**Format guarantee:** Minor version bumps add fields or values (backward compatible). Major version bumps may remove or rename fields (breaking).

---

## Common Structure

All catalogs share these top-level fields:

```json
{
  "$ontology_id": "catalog_name",
  "$schema_version": "1.0.0",
  // ... catalog-specific fields follow
}
```

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `$ontology_id` | string | Yes | Unique identifier for the catalog |
| `$schema_version` | string | Yes | SemVer version of this catalog's schema |

---

## Catalog: attributes

**File:** `ontology/catalogs/attributes.json`  
**$ontology_id:** `attributes`  
**$schema_version:** `1.0.0`

Defines canonical classifications for firm type and investment/operational focus.

### Schema

```json
{
  "$ontology_id": "attributes",
  "$schema_version": "1.0.0",
  "firm_type": [
    {
      "value": "private_equity",
      "description": "A private equity firm that invests in private companies through buyouts, growth equity, or venture capital strategies."
    },
    // ... more firm_type entries
  ],
  "focus": [
    {
      "value": "commercial_real_estate",
      "description": "Investment, development, or operation of income-producing properties such as office, retail, industrial, and multifamily assets."
    },
    // ... more focus entries
  ]
}
```

### Fields

#### `firm_type` (array)

List of firm type classifications. Each entry has:

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `value` | string | Yes | `"private_equity"` |
| `description` | string | Yes | `"A private equity firm..."` |

**Constraints:**
- `value` must be unique within the `firm_type` array
- `value` must be snake_case (lowercase letters, numbers, underscores only)
- `description` should be 1-3 sentences

**Examples:**
```json
{
  "value": "family_office",
  "description": "A private wealth management entity that manages the investments and financial affairs of a single ultra-high-net-worth family."
}
```

#### `focus` (array)

List of focus/industry classifications. Structure identical to `firm_type`.

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `value` | string | Yes | `"commercial_real_estate"` |
| `description` | string | Yes | `"Investment, development..."` |

**Examples:**
```json
{
  "value": "technology",
  "description": "Software, hardware, semiconductors, and technology-enabled services companies across the technology sector."
}
```

### Usage

```python
from ontology.registry import get_catalog

attrs = get_catalog("attributes")

# Iterate firm types
for entry in attrs["firm_type"]:
    print(f"{entry['value']}: {entry['description']}")

# Build lookup map
firm_types_by_value = {e["value"]: e["description"] for e in attrs["firm_type"]}

# Validate an input
if user_input_firm_type not in firm_types_by_value:
    raise ValueError(f"Invalid firm_type: {user_input_firm_type}")
```

---

## Catalog: naics

**File:** `ontology/catalogs/naics.json`  
**$ontology_id:** `naics`  
**$schema_version:** `1.0.0`

Defines North American Industry Classification System (NAICS) sector classifications.

### Schema

```json
{
  "$ontology_id": "naics",
  "$schema_version": "1.0.0",
  "naics_sectors": [
    {
      "code": "11",
      "title": "Agriculture, Forestry, Fishing and Hunting",
      "description": "Industries engaged in growing crops, raising animals, harvesting timber, and harvesting fish and other animals from farms or natural habitats."
    },
    // ... more sectors
  ]
}
```

### Fields

#### `naics_sectors` (array)

List of NAICS sector classifications. Each entry has:

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `code` | string | Yes | `"11"`, `"31-33"` |
| `title` | string | Yes | `"Agriculture, Forestry, Fishing and Hunting"` |
| `description` | string | Yes | `"Industries engaged in..."` |

**Constraints:**
- `code` must be unique within the `naics_sectors` array
- `code` is a NAICS sector code (2 digits or digit-digit range)
- `title` is the official NAICS sector title
- `description` should be 1-2 sentences

**Examples:**
```json
{
  "code": "21",
  "title": "Mining, Quarrying, and Oil and Gas Extraction",
  "description": "Industries that extract naturally occurring minerals, oil, and gas; includes quarrying, drilling, and support services."
}
```

### Usage

```python
from ontology.registry import get_catalog

naics = get_catalog("naics")

# Build code → sector map
sectors_by_code = {e["code"]: e for e in naics["naics_sectors"]}

# Look up a sector
if "22" in sectors_by_code:
    sector = sectors_by_code["22"]
    print(f"{sector['code']}: {sector['title']}")
```

---

## Catalog: activity_cycle

**File:** `ontology/catalogs/activity_cycle.json`  
**$ontology_id:** `activity_cycle`  
**$schema_version:** `1.0.0`

Defines a hierarchical taxonomy of business activities and processes based on the CHG activity cycle model.

### Schema

```json
{
  "$ontology_id": "activity_cycle",
  "$schema_version": "1.0.0",
  "ActivityCycle": [
    {
      "ActivityID": "1.1.1",
      "Phase": "1 Procures",
      "Part": "1.1 Sources",
      "Section": "1.1.1",
      "FormalDefinition": "Collects and synthesizes all information relevant to purchasing decisions; Identifies and recruits potential suppliers of the resources necessary for Researches production",
      "Colloquial": "Researches potential purchases",
      "Examples": "Procurement Consulting, Supply Chain Research",
      "IO": "C2i, C2ii, C2iii, C3ii, C3iii"
    },
    // ... more activities
  ]
}
```

### Fields

#### `ActivityCycle` (array)

List of activity definitions. Each entry has:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ActivityID` | string | Yes | Unique hierarchical identifier (e.g., `"1.1.1"`) |
| `Phase` | string | Yes | High-level phase (e.g., `"1 Procures"`) |
| `Part` | string | Yes | Subdivision within phase (e.g., `"1.1 Sources"`) |
| `Section` | string | Yes | Fine-grained section (same as ActivityID) |
| `FormalDefinition` | string | Yes | Formal, technical definition |
| `Colloquial` | string | Yes | Human-friendly description |
| `Examples` | string | Yes | Comma-separated list of real-world examples |
| `IO` | string | Yes | Input/Output references (e.g., `"C2i, C2ii"`) |

**Constraints:**
- `ActivityID` must be unique
- `ActivityID` follows pattern: `[1-9]+\.[0-9]+\.[0-9]+` (hierarchical levels)
- `FormalDefinition` should be 1-3 sentences
- `Colloquial` should be brief (one phrase)
- `Examples` is comma-separated, no trailing comma
- `IO` is comma-separated reference codes

**Examples:**
```json
{
  "ActivityID": "2.2.2",
  "Phase": "2 Produces",
  "Part": "2.2 Makes",
  "Section": "2.2.2",
  "FormalDefinition": "Produces the product",
  "Colloquial": "Makes the product",
  "Examples": "Manufacturing, Software Developers, Food Producers, Construction",
  "IO": "n/a"
}
```

### Usage

```python
from ontology.registry import get_catalog

activity = get_catalog("activity_cycle")

# Build ActivityID → entry map
activities_by_id = {e["ActivityID"]: e for e in activity["ActivityCycle"]}

# Look up an activity
if "1.1.1" in activities_by_id:
    act = activities_by_id["1.1.1"]
    print(f"{act['ActivityID']}: {act['Colloquial']}")

# Filter by Phase
procures_activities = [
    e for e in activity["ActivityCycle"]
    if e["Phase"] == "1 Procures"
]
```

---

## Defining New Catalogs (Future)

When adding new catalogs in future phases, follow these guidelines:

### Metadata Requirements

Every catalog must include:
```json
{
  "$ontology_id": "unique_name",
  "$schema_version": "1.0.0",
  // ... custom fields
}
```

### Naming Conventions

- `$ontology_id`: snake_case, globally unique
- `field_name`: snake_case
- `value` fields: snake_case, lowercase
- `description` fields: Title case, 1-3 sentences

### Version Bumping

When modifying a catalog:

**Patch (1.0.0 → 1.0.1):**
- Fix typos in descriptions
- Clarify existing definitions
- No structural changes

**Minor (1.0.0 → 1.1.0):**
- Add new values to existing arrays
- Add optional new fields to entries
- Always backward compatible

**Major (1.0.0 → 2.0.0):**
- Remove or rename values
- Remove or rename fields
- Change entry structure
- Requires consumer code review

---

## Validation

### JSON Schema (Future)

Each catalog will have an associated JSON Schema for validation. Currently enforced manually in code review.

### Best Practices

1. **Uniqueness:** Values must be unique within their arrays
2. **Completeness:** All required fields must be present
3. **Formatting:** Snake_case identifiers, proper description sentences
4. **Examples:** Descriptions should include real-world examples
5. **Testing:** CI should validate against schema before merge

---

## Examples: Building from Catalogs

### Extract All Values

```python
from ontology.registry import get_catalog

attrs = get_catalog("attributes")

# All firm_type values
firm_types = [e["value"] for e in attrs["firm_type"]]
# => ["actuary", "administrator", "advisor", ... ]
```

### Build Graphical Selector

```python
from ontology.registry import get_catalog

def build_form_options(catalog_name: str, field: str) -> list[dict]:
    """Build HTML <option> elements."""
    catalog = get_catalog(catalog_name)
    return [
        {
            "value": entry["value"],
            "label": entry["description"],
        }
        for entry in catalog.get(field, [])
    ]

# Usage:
firm_type_options = build_form_options("attributes", "firm_type")
# => [
#     {"value": "private_equity", "label": "A private equity firm..."},
#     ...
#   ]
```

### Filter by Pattern

```python
from ontology.registry import get_catalog
import re

attrs = get_catalog("attributes")

# Find all real estate related values
for entry in attrs["focus"]:
    if re.search(r"real\s*estate", entry["description"], re.I):
        print(entry["value"])
```

---

## Support & Maintenance

All catalogs are maintained in the `ontology-core` repository. Proposed changes should:

1. Open an issue describing the change
2. Create a PR with the modified catalog JSON
3. Include a migration guide if breaking
4. Update `CHANGELOG.md` with the change
5. Bump the catalog's `$schema_version`

