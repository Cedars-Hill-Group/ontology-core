# Ontology Core Documentation

This directory contains comprehensive documentation for the `ontology-core` package and its integration with downstream applications.

---

## For Consumers (Downstream Applications)

Start here if you're integrating `ontology-core` into your project.

### [Integration Guide](INTEGRATION.md)

**Best for:** Getting started, common patterns, troubleshooting

- Quick start with minimal usage
- Complete workflow examples (validation, UI, database, LLM)
- Testing patterns
- Configuration and startup checks
- Migration from legacy code

### [API Reference](API.md)

**Best for:** Understanding the exact behavior of each function

- `get_catalog(name, version=None)` — load a catalog
- `list_catalogs()` — enumerate available catalogs
- `get_catalog_version(name)` — get schema version
- Catalog formats (attributes, naics, activity_cycle)
- Versioning strategy and compatibility checking
- Error handling and performance
- Integration patterns

---

## For Repository Maintainers

Documentation about the ontology-core architecture and maintenance.

### [Catalog Format Specification](CATALOG_FORMAT.md)

**Best for:** Understanding catalog structure, adding new catalogs, validating changes

- Formal structure of all catalogs
- Field requirements and constraints
- Naming conventions
- Version bumping rules
- Validation guidelines
- How to add new catalogs

---

## Quick Links

### Installation

```bash
pip install git+https://github.com/rounder22/ontology-core.git@v0.2.0
```

### Minimal Example

```python
from ontology.registry import get_catalog, list_catalogs

# See all available catalogs
print(list_catalogs())  # ["attributes", "naics", "activity_cycle"]

# Load a catalog
attributes = get_catalog("attributes")

# Access values
for entry in attributes["firm_type"]:
    print(f"{entry['value']}: {entry['description']}")
```

### Next Steps

1. Read [Integration Guide](INTEGRATION.md) for your use case
2. Reference [API Reference](API.md) for detailed function docs
3. Check [Catalog Format](CATALOG_FORMAT.md) for catalog structures
4. Look at [examples/](#examples) for complete runnable code (coming soon)

---

## FAQ

**Q: Do I need a knowledge base to use catalogs?**

A: No. Use `get_catalog()` for standalone access to catalogs. Entity classes are optional and only needed if you have Markdown knowledge base files.

**Q: How do I validate user input against a catalog?**

A: See [Integration Guide: Validate User Input](INTEGRATION.md#1-validate-user-input-against-catalogs)

**Q: What if I need a new catalog or field?**

A: Open an issue on GitHub. See [Catalog Format: Support & Maintenance](CATALOG_FORMAT.md#support--maintenance)

**Q: How do I pin to a specific ontology version?**

A: Pin the package version in your dependency spec. Catalogs are versioned separately in `$schema_version` fields. See [API Reference: Versioning](API.md#versioning)

**Q: Can I modify catalog behavior in my application?**

A: You can wrap/extend the registry functions, but catalog content itself is read-only. See [Catalog Format](CATALOG_FORMAT.md) for the canonical definition.

---

## Support

- **Bug reports:** https://github.com/rounder22/ontology-core/issues
- **Pull requests:** https://github.com/rounder22/ontology-core/pulls
- **Documentation issues:** Add label `docs` to your issue

