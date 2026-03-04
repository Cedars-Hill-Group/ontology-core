# Commercial Real Estate Schema — Output

## Purpose
Specify the normalised output format produced by the data ingestion and
integration layer for entities processed under the **commercial_real_estate**
schema.

## Output Object Shape

```json
{
  "entity_type": "company | person | project",
  "schema": "commercial_real_estate",
  "name": "Apex Real Estate Partners",
  "firm_type": ["real_estate_developer"],
  "focus": ["commercial_real_estate"],
  "website": "https://apexrep.example.com",
  "headquarters": "Dallas, TX",
  "description": "A value-add CRE firm focused on office and industrial assets in the Sun Belt.",
  "founded": "2010",
  "employees": "25-50",
  "linkedin": "https://linkedin.com/company/apex-rep",
  "property_types": ["office", "industrial"],
  "asset_class": "value_add",
  "geography": ["Texas", "Florida", "Georgia"],
  "aum": "$2.5B",
  "total_sf": "12,000,000",
  "deal_size_range": "$20M - $150M",
  "equity_check": "$10M - $50M",
  "debt_types": ["senior", "mezzanine"],
  "hold_period": "3-5 years",
  "leverage_target": "60-70% LTV",
  "preferred_markets": ["Dallas", "Austin", "Miami", "Atlanta"],
  "extra_metadata": {},
  "source_file": "companies/apex-real-estate-partners.md",
  "schema_version": "1.0.0"
}
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `entity_type` | ✅ | One of `company`, `person`, `project` |
| `schema` | ✅ | Always `"commercial_real_estate"` for this schema |
| `name` | ✅ | Normalised entity name |
| `firm_type` | ✅ | List of normalised firm-type ontology values |
| `focus` | ✅ | List of normalised focus ontology values |
| `website` | ❌ | Website URL |
| `headquarters` | ❌ | Primary office location |
| `description` | ❌ | Short narrative description |
| `founded` | ❌ | Founding year or date |
| `employees` | ❌ | Approximate employee count or band |
| `linkedin` | ❌ | LinkedIn profile or company page URL |
| `property_types` | ❌ | Asset types targeted (office, retail, industrial, multifamily, …) |
| `asset_class` | ❌ | Risk/return profile (core, core_plus, value_add, opportunistic) |
| `geography` | ❌ | Target markets, regions, states, or countries |
| `aum` | ❌ | Assets under management |
| `total_sf` | ❌ | Total square footage owned or managed |
| `deal_size_range` | ❌ | Typical transaction size range |
| `equity_check` | ❌ | Typical equity cheque size |
| `debt_types` | ❌ | Debt instruments used (senior, mezzanine, preferred equity) |
| `hold_period` | ❌ | Target asset hold period |
| `leverage_target` | ❌ | Target LTV or LTC range |
| `preferred_markets` | ❌ | Specific MSAs or submarkets of interest |
| `extra_metadata` | ✅ | Catch-all for unrecognised front matter fields |
| `source_file` | ✅ | Relative path to the originating Markdown file |
| `schema_version` | ✅ | Semantic version of this output schema |
