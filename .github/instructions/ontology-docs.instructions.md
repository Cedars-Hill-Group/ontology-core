---
description: "Use when editing repository documentation in docs/ or schemas/. Keeps ontology-core docs concise, structured, and aligned with catalog/output terminology."
name: "ontology-core documentation conventions"
applyTo:
  - "docs/**/*.md"
  - "schemas/**/*.md"
  - "README.md"
---
# ontology-core Documentation Conventions

## Audience and structure

- Write for engineers integrating or extending ontology-core.
- Start sections with intent first, then concrete formats or examples.
- Keep headings task-oriented (for example: Build Outputs, Catalog Fields, Validation Rules).

## Terminology consistency

- Use repository terms consistently: ontology, objects, links, manifest, catalogs, entities.
- Keep file names and keys exact when referencing JSON artifacts.
- Distinguish clearly between source schema templates and generated outputs.

## Format guidance

- Prefer short sections, bullet lists, and examples over long narrative paragraphs.
- When describing data formats, include concise field tables or key lists.
- Keep examples minimal but executable by copy/paste when possible.

## Change safety

- When behavior changes, update docs in the same change where possible.
- Call out backward-incompatible changes explicitly.
- Do not document hypothetical fields or pipeline behavior not present in code.
