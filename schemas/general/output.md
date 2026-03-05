# General Schema — Output

## Purpose
Specify the normalised output format that the data ingestion and integration
layer produces for entities processed under the **general** schema.  Downstream
services (domain services layer, LLM pipelines, application layer) should
expect this structure.

## Output Object Shape

```json
{
  "entity_type": "company | person | project",
  "schema": "general",
  "name": "Acme Capital Partners",
  "firm_type": ["private_equity"],
  "focus": ["technology", "healthcare"],
  "website": "https://acmecapital.example.com",
  "headquarters": "New York, NY",
  "description": "A growth-equity firm focused on technology and healthcare.",
  "founded": "2005",
  "employees": "50-100",
  "linkedin": "https://linkedin.com/company/acme-capital",
  "extra_metadata": {},
  "source_file": "companies/acme-capital-partners.md",
  "schema_version": "1.0.0"
}
```

## Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `entity_type` | ✅ | One of `company`, `person`, `project` |
| `schema` | ✅ | Always `"general"` for this schema |
| `name` | ✅ | Normalised entity name |
| `firm_type` | ✅ | List of normalised firm-type ontology values |
| `focus` | ✅ | List of normalised focus ontology values |
| `website` | ❌ | Company or personal website URL |
| `headquarters` | ❌ | Primary office location |
| `description` | ❌ | Short narrative description |
| `founded` | ❌ | Founding year or date |
| `employees` | ❌ | Approximate employee count or band |
| `linkedin` | ❌ | LinkedIn profile or company page URL |
| `extra_metadata` | ✅ | Catch-all for unrecognised front matter fields |
| `source_file` | ✅ | Relative path to the originating Markdown file |
| `schema_version` | ✅ | Semantic version of this output schema |
