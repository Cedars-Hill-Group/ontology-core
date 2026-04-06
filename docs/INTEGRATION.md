# Integration Guide for Downstream Applications

This guide helps downstream applications integrate with `ontology-core` catalogs.

---

## Installation

### In Your Project

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "ontology-core @ git+https://github.com/rounder22/ontology-core.git@v0.2.0",
]
```

Or with pip:

```bash
pip install git+https://github.com/rounder22/ontology-core.git@v0.2.0
```

### Version Pinning

Always pin to a specific version tag (e.g., `@v0.2.0`) for reproducible builds. Use tags in the form `vX.Y.Z` for package versions.

---

## Quick Start

### Minimal Usage (Catalogs Only)

```python
from ontology.registry import get_catalog, list_catalogs

# See all available catalogs
print(list_catalogs())  # ["attributes", "naics", "activity_cycle"]

# Load a catalog
attributes = get_catalog("attributes")

# Access values
for firm_type in attributes["firm_type"]:
    print(f"{firm_type['value']}: {firm_type['description']}")
```

### With Entity Support (Optional)

If you also load entities from Markdown files:

```python
from ontology.entities.company import Company
from ontology.registry import get_catalog

# Load catalogs
attrs = get_catalog("attributes")

# Load entities from knowledge base
companies = Company.iter_directory("/path/to/kb/companies")
for company in companies:
    print(company.name, company.firm_type)
    # In Phase 2+, validation against catalogs will be automatic
```

---

## Common Workflows

### 1. Validate User Input Against Catalogs

```python
from ontology.registry import get_catalog

class FirmValidator:
    def __init__(self):
        self.attrs = get_catalog("attributes")
        self.firm_types = {e["value"] for e in self.attrs["firm_type"]}
    
    def is_valid_firm_type(self, value: str) -> bool:
        return value in self.firm_types
    
    def get_description(self, firm_type: str) -> str:
        for entry in self.attrs["firm_type"]:
            if entry["value"] == firm_type:
                return entry["description"]
        raise ValueError(f"Unknown firm_type: {firm_type}")

validator = FirmValidator()
if not validator.is_valid_firm_type("private_equity"):
    raise ValueError("Invalid firm type")
description = validator.get_description("private_equity")
```

### 2. Generate Dropdown Options for UI

**FastAPI / Pydantic example:**

```python
from pydantic import BaseModel, field_validator
from ontology.registry import get_catalog
from typing import Literal

class CompanyInput(BaseModel):
    name: str
    firm_type: str
    focus: list[str]
    
    @field_validator("firm_type")
    @classmethod
    def validate_firm_type(cls, v):
        attrs = get_catalog("attributes")
        valid = {e["value"] for e in attrs["firm_type"]}
        if v not in valid:
            raise ValueError(f"Invalid firm_type: {v}")
        return v

# In your route:
@app.get("/api/enums/firm-types")
def get_firm_types():
    """Return enum options for dropdown."""
    attrs = get_catalog("attributes")
    return [
        {"value": e["value"], "label": e["description"]}
        for e in attrs["firm_type"]
    ]
```

### 3. Database Schema Generation

**SQLAlchemy example:**

```python
from ontology.registry import get_catalog
from sqlalchemy import Column, String, Enum, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def get_firm_type_enum(engine):
    """Generate SQLAlchemy enum from catalog."""
    attrs = get_catalog("attributes")
    values = [e["value"] for e in attrs["firm_type"]]
    return Enum(*values, name="firm_type")

FirmTypeEnum = get_firm_type_enum(engine)

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    firm_type = Column(FirmTypeEnum, nullable=False)
```

**Django example:**

```python
from ontology.registry import get_catalog
from django.db import models

def get_firm_type_choices():
    """Generate Django choices from catalog."""
    attrs = get_catalog("attributes")
    return [
        (e["value"], e["description"])
        for e in attrs["firm_type"]
    ]

class Company(models.Model):
    name = models.CharField(max_length=255)
    firm_type = models.CharField(
        max_length=100,
        choices=get_firm_type_choices(),
    )
```

### 4. LLM Classification Prompts

```python
from ontology.registry import get_catalog
import anthropic

def classify_firm_type_with_llm(description: str) -> str:
    """Use Claude to classify firm type."""
    attrs = get_catalog("attributes")
    
    # Build options text
    options = "\n".join([
        f"- {e['value']}: {e['description']}"
        for e in attrs["firm_type"]
    ])
    
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""Classify the following company description as one of these firm_type values:

{options}

Company: {description}

Respond with ONLY the firm_type value."""
            }
        ]
    )
    
    return message.content[0].text.strip()
```

### 5. Generate API Documentation

```python
from ontology.registry import get_catalog, list_catalogs
import json

def generate_catalog_docs():
    """Generate markdown documentation of all catalogs."""
    docs = "# Ontology Catalogs\n\n"
    
    for catalog_name in list_catalogs():
        catalog = get_catalog(catalog_name)
        docs += f"## {catalog_name}\n"
        docs += f"**Version:** {catalog['$schema_version']}\n\n"
        
        # Document structure
        docs += "### Values\n"
        for key, values in catalog.items():
            if key.startswith("$"):
                continue
            if isinstance(values, list):
                docs += f"#### {key}\n"
                for entry in values:
                    docs += f"- `{entry['value']}`: {entry['description']}\n"
    
    return docs

print(generate_catalog_docs())
```

### 6. Configuration and Startup Checks

```python
from ontology.registry import get_catalog, get_catalog_version
from packaging import version as pkg_version
import logging

logger = logging.getLogger(__name__)

def validate_ontology_compatibility():
    """Validate that catalogs meet minimum requirements."""
    requirements = {
        "attributes": "1.0.0",
        "naics": "1.0.0",
    }
    
    errors = []
    for catalog_name, min_version in requirements.items():
        try:
            actual = get_catalog_version(catalog_name)
            if pkg_version.parse(actual) < pkg_version.parse(min_version):
                errors.append(
                    f"{catalog_name}: {actual} < {min_version} (required)"
                )
            else:
                logger.info(f"{catalog_name} version: {actual} ✓")
        except FileNotFoundError:
            errors.append(f"{catalog_name}: NOT FOUND")
    
    if errors:
        raise RuntimeError("Ontology validation failed:\n" + "\n".join(errors))

# Call at startup
if __name__ == "__main__":
    validate_ontology_compatibility()
    # Now safe to use catalogs
```

---

## Testing with Catalogs

### Unit Tests

```python
import pytest
from ontology.registry import get_catalog, CatalogRegistry

@pytest.fixture(autouse=True)
def clear_catalog_cache():
    """Clear cache before each test."""
    CatalogRegistry.clear_cache()
    yield
    CatalogRegistry.clear_cache()

def test_firm_type_validation():
    attrs = get_catalog("attributes")
    firm_types = {e["value"] for e in attrs["firm_type"]}
    
    assert "private_equity" in firm_types
    assert "unknown_type" not in firm_types

def test_catalog_has_descriptions():
    attrs = get_catalog("attributes")
    for entry in attrs["firm_type"]:
        assert entry.get("description"), f"Missing description for {entry['value']}"
```

### Mocking for Testing

```python
from unittest import mock
from ontology.registry import get_catalog

# For testing without loading real catalogs
mock_catalog = {
    "$ontology_id": "attributes",
    "$schema_version": "1.0.0",
    "firm_type": [
        {"value": "test_type", "description": "Test firm type"}
    ],
    "focus": [],
}

with mock.patch("ontology.registry.get_catalog", return_value=mock_catalog):
    result = get_catalog("attributes")
    assert result["firm_type"][0]["value"] == "test_type"
```

---

## Environment-Specific Configuration

### Per-Environment Catalog Versions

```python
import os
from ontology.registry import get_catalog_version

ENV = os.getenv("ENVIRONMENT", "development")

# Different requirements per environment
CATALOG_REQUIREMENTS = {
    "development": {
        "attributes": "1.0.0",
    },
    "staging": {
        "attributes": "1.1.0",
    },
    "production": {
        "attributes": "1.2.0",
    },
}

versions = CATALOG_REQUIREMENTS.get(ENV, {})
for catalog, required_version in versions.items():
    actual = get_catalog_version(catalog)
    assert actual >= required_version
```

---

## Troubleshooting

### "Catalog not found" Error

```
FileNotFoundError: Catalog 'wrong_name' not found in ontology.catalogs
```

**Solution:** Check the available catalogs:

```python
from ontology.registry import list_catalogs
print(list_catalogs())  # ["attributes", "naics", "activity_cycle"]
```

### Stale Cached Data

If you modify catalogs during development and see old data:

```python
from ontology.registry import CatalogRegistry
CatalogRegistry.clear_cache()
```

### Import Errors

If you get `ModuleNotFoundError: No module named 'ontology'`:

1. Ensure the package is installed: `pip list | grep ontology-core`
2. If installing from GitHub, verify the URL: `pip install git+https://github.com/rounder22/ontology-core.git@v0.2.0`
3. Reinstall if needed: `pip install --force-reinstall git+...`

### Catalog Format Changes

If a catalog structure changes unexpectedly:

```python
from ontology.registry import get_catalog_version
v = get_catalog_version("attributes")
print(f"Using catalog version: {v}")

# Compare to your expected version
expected = "1.0.0"
if v != expected:
    print(f"WARNING: Expected {expected}, got {v}")
```

---

## Best Practices

1. **Pin versions:** Always pin to specific package versions in production
2. **Validate at startup:** Check catalog compatibility when your app starts
3. **Cache lookups:** Don't call `get_catalog()` inside loops; cache the result
4. **Handle errors:** Wrap catalog access in try/except blocks
5. **Use safe access:** Use `.get()` and safe iteration to handle missing keys
6. **Document assumptions:** Comment which catalog fields your code depends on
7. **Test validation:** Unit test that your validation logic works correctly
8. **Monitor versions:** Log the catalog versions your app is using for debugging

---

## Migration from Legacy Code

### If You Used PropertyCollector

**Old code (removed):**
```python
from ontology.properties.collector import PropertyCollector
collector = PropertyCollector("/path/to/kb")
catalog = collector.collect()
```

**New code:**
```python
from ontology.registry import get_catalog
catalog = get_catalog("attributes")
```

### If You Used PropertyCatalog

**Old code (removed):**
```python
from ontology.properties.models import PropertyCatalog
catalog = PropertyCatalog.load("properties.json")
for pv in catalog.firm_type:
    print(pv.value, pv.description)
```

**New code:**
```python
from ontology.registry import get_catalog
catalog = get_catalog("attributes")
for entry in catalog["firm_type"]:
    print(entry["value"], entry["description"])
```

---

## Next Steps

- Read the [API Reference](API.md) for detailed function documentation
- Explore [Catalog Formats](CATALOG_FORMAT.md) for the structure of each catalog
- Check the [examples/](../examples/) directory for complete runnable examples

