# Commercial Real Estate Schema — Extraction

## Purpose
Define what information the data ingestion and integration layer should extract
for entities associated with the **commercial_real_estate** schema.  This schema
extends the general schema with CRE-specific fields.

## Fields to Extract

### General Fields (inherited)
See `schemas/general/extraction.md` for the base set of fields that apply to
all entities regardless of schema.

### CRE-Specific Fields

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `property_types` | list | front matter | e.g. `office`, `retail`, `industrial`, `multifamily` |
| `asset_class` | string | front matter | e.g. `core`, `core_plus`, `value_add`, `opportunistic` |
| `geography` | string \| list | front matter | Target markets or regions |
| `aum` | string | front matter | Assets under management (formatted string or number) |
| `total_sf` | string | front matter | Total square footage owned / managed |
| `deal_size_range` | string | front matter | Typical transaction size range |
| `equity_check` | string | front matter | Typical equity cheque size |
| `debt_types` | list | front matter | e.g. `senior`, `mezzanine`, `preferred_equity` |
| `hold_period` | string | front matter | Target hold period (e.g. `3-5 years`) |
| `leverage_target` | string | front matter | Target LTV or LTC range |
| `preferred_markets` | list | front matter | List of preferred MSAs or regions |

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
