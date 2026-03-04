# General Schema — Extraction

## Purpose
Define what information the data ingestion and integration layer should extract
for entities associated with the **general** schema.  This schema applies to
companies, people, and projects that do not require a more specialised schema
(e.g. `commercial_real_estate`).

## Fields to Extract

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `name` | string | front matter | Legal or common name |
| `firm_type` | string \| list | front matter | Normalised to ontology values |
| `focus` | string \| list | front matter | Normalised to ontology values |
| `website` | string | front matter | Optional |
| `headquarters` | string | front matter | City, State / Country |
| `description` | string | front matter or body | Brief narrative |
| `founded` | string | front matter | Year or date |
| `employees` | string | front matter | Approximate headcount |
| `linkedin` | string | front matter | Profile or company page URL |

## Extraction Rules

1. All front matter fields are read verbatim and then normalised by the
   ontology layer before storage.
2. If `description` is absent from front matter the first non-empty paragraph
   of the Markdown body is used.
3. Multi-value fields (`firm_type`, `focus`) may be stored as YAML lists or as
   a single comma-separated string; the ingestion layer must split and trim each
   value before normalisation.
4. Unknown fields found in front matter are passed through as-is under an
   `extra_metadata` key so that no information is silently discarded.
