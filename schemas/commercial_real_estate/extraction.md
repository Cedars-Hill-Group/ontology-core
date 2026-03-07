Use this schema to extract information about companies operating in the commercial real estate industry, including lenders, brokers, investors, developers, and advisors.

# Purpose
Define what information the data ingestion and integration layer should extract
for entities associated with the **commercial_real_estate** schema.  This schema
extends the general schema with CRE-specific fields.

## Fields to Extract

# General Fields (inherited)
See `schemas/general/extraction.md` for the base set of fields that apply to
all entities regardless of schema.

# CRE-Specific Fields

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `prop_type` | string \| list | front matter | Normalized to ontology values |
| `loan_type` | string \| list | front matter | Normalized to ontology values |
| `loan_structure` | string \| list | front matter | Normalized to ontology values |
| `loan_purpose` | string \| list | front matter | Normalized to ontology values |
| `project_type` | string \| list | front matter | Normalized to ontology values |

## Extraction Rules

1. All general extraction rules apply (see `schemas/general/extraction.md`).
2. `property_types` must be normalised to the canonical ontology values.
3. `aum` and financial figures are stored as strings to preserve the original
   notation; the data layer is responsible for parsing into numeric types.
4. Geographic fields accept free-form text, MSA names, state codes, or country
   names; normalisation to ISO codes happens in the integration layer.
5. Any `firm_type` value of `real_estate_developer`, `reit`, or
   `real_estate_investment_trust` triggers automatic selection of this schema
   when no explicit schema is set.
