---
description: "Use when creating or editing Python code in ontology-core, including entities, registry loaders, build pipeline code, and tests. Applies preferred project typing, docstring, modeling, and test conventions."
name: "ontology-core Python conventions"
applyTo: "**/*.py"
---
# ontology-core Python Conventions

## Imports and typing

- Prefer starting modules with `from __future__ import annotations`.
- Prefer Python 3.10+ union syntax (`X | None`) instead of `Optional[X]`.
- Keep type hints on public functions and dataclass fields.

## Docstrings and API contracts

- Prefer NumPy-style docstrings for public classes and functions.
- Include `Parameters`, `Returns`, and `Raises` sections when relevant.
- Keep `@property` docstrings short and outcome-focused.

## Entity and model patterns

- Prefer `@property` accessors for normalized metadata values.
- Reuse shared conversion helpers such as `as_list` instead of ad hoc normalization.
- Use dataclasses for record-like build artifacts and manifests.

## Test conventions

- Group tests by component using `Test...` classes.
- Use fixtures from `tests/conftest.py` for reusable markdown/YAML sample data.
- Prefer deterministic assertions on entity IDs, labels, links, and serialized output shapes.

## Build and output expectations

- Preserve manifest-driven output behavior in pipeline changes.
- Keep output artifact structure consistent (`ontology.json`, `objects.json`, `links.json`, `manifest.json`).
- Avoid changing output schema or key names unless required by an intentional versioned change.

## Style and safety

- Follow Ruff constraints from `pyproject.toml` (line length 100, import order, pyflakes checks).
- Make minimal, targeted edits; avoid broad refactors unless explicitly requested.
- Preserve validation and error signaling behavior in loaders and entity parsing paths unless a task explicitly changes it.
