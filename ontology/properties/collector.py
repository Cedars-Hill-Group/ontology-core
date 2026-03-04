"""Property value collector.

Walks the knowledge-base directory, reads every Markdown entity file, collects
all unique values from the ``firm_type`` and ``focus`` front-matter fields,
cleans and normalises them, and returns a :class:`~ontology.properties.models.PropertyCatalog`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.project import Project
from ontology.properties.models import PropertyCatalog, PropertyValue

# ---------------------------------------------------------------------------
# Default descriptions — auto-generated descriptions are enriched here so that
# downstream LLMs receive meaningful context even for newly discovered values.
# Extend this dictionary as the ontology grows.
# ---------------------------------------------------------------------------

_FIRM_TYPE_DESCRIPTIONS: dict[str, str] = {
    "private_equity": (
        "A private equity firm that invests in private companies through "
        "buyouts, growth equity, or venture capital strategies."
    ),
    "family_office": (
        "A private wealth management entity that manages the investments and "
        "financial affairs of a single ultra-high-net-worth family."
    ),
    "multi_family_office": (
        "A wealth management firm that serves multiple high-net-worth families, "
        "providing investment, tax, and estate-planning services."
    ),
    "hedge_fund": (
        "An actively managed investment fund that employs a wide range of "
        "strategies to generate alpha, including long/short, macro, and arbitrage."
    ),
    "real_estate_investment_trust": (
        "A company that owns, operates, or finances income-producing real estate "
        "and is required to distribute the majority of its taxable income."
    ),
    "reit": (
        "A company that owns, operates, or finances income-producing real estate "
        "and is required to distribute the majority of its taxable income."
    ),
    "real_estate_developer": (
        "A firm that acquires land or existing structures and develops, "
        "renovates, or repositions real estate assets."
    ),
    "investment_bank": (
        "A financial institution that advises on and facilitates capital markets "
        "transactions, mergers and acquisitions, and other corporate finance activity."
    ),
    "commercial_bank": (
        "A bank that provides lending, deposit, and treasury services primarily "
        "to business and institutional clients."
    ),
    "insurance_company": (
        "A firm that underwrites risk products and manages a large investment "
        "portfolio to back policyholder liabilities."
    ),
    "sovereign_wealth_fund": (
        "A state-owned investment fund that manages national savings or commodity "
        "revenues for long-term returns."
    ),
    "pension_fund": (
        "An institutional investor that manages pooled contributions to provide "
        "retirement income to beneficiaries."
    ),
    "endowment": (
        "A portfolio of investments, typically held by a university, foundation, "
        "or nonprofit, managed to fund ongoing operations in perpetuity."
    ),
    "asset_manager": (
        "A firm that manages investment portfolios on behalf of institutional or "
        "retail clients across a range of asset classes."
    ),
    "operating_company": (
        "A business that generates revenue through the production, sale, or "
        "delivery of goods and services rather than through investment activity."
    ),
    "other": (
        "A firm type that does not fit neatly into any of the standard categories "
        "defined in the ontology."
    ),
}

_FOCUS_DESCRIPTIONS: dict[str, str] = {
    "commercial_real_estate": (
        "Investment, development, or operation of income-producing properties "
        "such as office, retail, industrial, and multifamily assets."
    ),
    "residential_real_estate": (
        "Development, acquisition, or management of single-family or "
        "small-multifamily residential properties."
    ),
    "industrial_real_estate": (
        "Warehouses, distribution centres, manufacturing facilities, and other "
        "logistics-oriented real estate assets."
    ),
    "retail_real_estate": (
        "Shopping centres, strip malls, high-street retail, and other "
        "consumer-facing commercial properties."
    ),
    "hospitality": (
        "Hotels, resorts, and short-term accommodation assets across "
        "lodging segments and geographies."
    ),
    "healthcare_real_estate": (
        "Medical office buildings, senior housing, life-sciences campuses, "
        "and other healthcare-related properties."
    ),
    "technology": (
        "Software, hardware, semiconductors, and technology-enabled services "
        "companies across the technology sector."
    ),
    "financial_services": (
        "Banks, insurance companies, asset managers, and other firms that "
        "provide financial products and services."
    ),
    "energy": (
        "Oil and gas, renewable energy, utilities, and other energy-sector "
        "businesses and infrastructure."
    ),
    "infrastructure": (
        "Long-lived physical assets including transportation networks, utilities, "
        "communications towers, and social infrastructure."
    ),
    "healthcare": (
        "Pharmaceutical, biotech, medical devices, and healthcare services "
        "companies across the healthcare industry."
    ),
    "consumer": (
        "Consumer goods, retail, and services businesses that sell directly or "
        "indirectly to end consumers."
    ),
    "industrials": (
        "Manufacturing, aerospace, defence, engineering services, and other "
        "industrial-sector businesses."
    ),
    "diversified": (
        "A broad, multi-sector investment mandate not concentrated in a single "
        "industry or asset class."
    ),
    "credit": (
        "Fixed-income, private credit, distressed debt, and other lending or "
        "credit-oriented investment strategies."
    ),
    "private_equity": (
        "Buyout, growth equity, and venture capital strategies targeting "
        "private companies."
    ),
    "venture_capital": (
        "Early-stage and growth-stage equity investment in high-potential "
        "startups and emerging companies."
    ),
    "other": (
        "A focus area that does not fit neatly into any of the standard "
        "categories defined in the ontology."
    ),
}


class PropertyCollector:
    """Collects and normalises ``firm_type`` and ``focus`` values from the knowledge base.

    Usage
    -----
    .. code-block:: python

        from ontology.properties.collector import PropertyCollector

        collector = PropertyCollector("/path/to/knowledge-base")
        catalog = collector.collect()
        catalog.save("output/properties.json")

    Parameters
    ----------
    knowledge_base_path:
        Root directory of the knowledge base.  The collector looks for
        subdirectories named ``companies``, ``people``, and ``projects``
        (configurable via *entity_dirs*).
    entity_dirs:
        Optional mapping of entity type to subdirectory name.  Defaults to
        ``{"companies": Company, "people": Person, "projects": Project}``.
    """

    _DEFAULT_ENTITY_DIRS: dict[str, type] = {
        "companies": Company,
        "people": Person,
        "projects": Project,
    }

    def __init__(
        self,
        knowledge_base_path: str | Path,
        entity_dirs: dict[str, type] | None = None,
    ) -> None:
        self._kb_path = Path(knowledge_base_path).resolve()
        self._entity_dirs = entity_dirs or self._DEFAULT_ENTITY_DIRS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect(self) -> PropertyCatalog:
        """Walk the knowledge base and return a :class:`PropertyCatalog`.

        All ``firm_type`` and ``focus`` front-matter values are normalised
        (lowercased, whitespace collapsed, spaces replaced with underscores)
        and deduplicated.  Each unique value is paired with a description
        from the built-in lookup table; unknown values receive an
        auto-generated placeholder description.
        """
        firm_type_values: dict[str, PropertyValue] = {}
        focus_values: dict[str, PropertyValue] = {}

        for subdir, entity_cls in self._entity_dirs.items():
            dir_path = self._kb_path / subdir
            if not dir_path.is_dir():
                continue

            entities = entity_cls.iter_directory(dir_path)
            for entity in entities:
                for raw in _collect_field(entity, "firm_type"):
                    key = _normalise(raw)
                    if key and key not in firm_type_values:
                        firm_type_values[key] = PropertyValue(
                            value=key,
                            description=_FIRM_TYPE_DESCRIPTIONS.get(
                                key,
                                f"A firm categorised as '{key}' within the ontology.",
                            ),
                        )
                for raw in _collect_field(entity, "focus"):
                    key = _normalise(raw)
                    if key and key not in focus_values:
                        focus_values[key] = PropertyValue(
                            value=key,
                            description=_FOCUS_DESCRIPTIONS.get(
                                key,
                                f"An investment or operational focus area categorised as '{key}'.",
                            ),
                        )

        return PropertyCatalog(
            firm_type=sorted(firm_type_values.values(), key=lambda pv: pv.value),
            focus=sorted(focus_values.values(), key=lambda pv: pv.value),
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_field(entity: Any, field: str) -> list[str]:
    """Return the raw values of *field* from *entity* as a list of strings."""
    value = entity.get(field)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _normalise(raw: str) -> str:
    """Clean and normalise a raw property value to a canonical snake_case key.

    Steps:
    1. Strip surrounding whitespace.
    2. Lower-case.
    3. Replace any run of whitespace or hyphens with a single underscore.
    4. Remove characters that are not alphanumeric or underscores.
    5. Collapse multiple underscores and strip leading/trailing underscores.
    """
    s = raw.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^\w]", "", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    return s
