"""Tests for the property collector and Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ontology.properties.collector import PropertyCollector, _normalise
from ontology.properties.models import PropertyCatalog, PropertyValue


class TestNormalise:
    def test_lowercase(self) -> None:
        assert _normalise("PrivateEquity") == "privateequity"

    def test_spaces_to_underscores(self) -> None:
        assert _normalise("private equity") == "private_equity"

    def test_hyphens_to_underscores(self) -> None:
        assert _normalise("family-office") == "family_office"

    def test_strips_whitespace(self) -> None:
        assert _normalise("  hedge fund  ") == "hedge_fund"

    def test_removes_special_chars(self) -> None:
        assert _normalise("real estate (commercial)") == "real_estate_commercial"

    def test_collapses_multiple_underscores(self) -> None:
        assert _normalise("a__b") == "a_b"

    def test_empty_string(self) -> None:
        assert _normalise("") == ""


class TestPropertyValue:
    def test_creation(self) -> None:
        pv = PropertyValue(value="private_equity", description="A PE firm.")
        assert pv.value == "private_equity"
        assert pv.description == "A PE firm."

    def test_serialisation(self) -> None:
        pv = PropertyValue(value="hedge_fund", description="A hedge fund.")
        data = json.loads(pv.model_dump_json())
        assert data["value"] == "hedge_fund"
        assert data["description"] == "A hedge fund."


class TestPropertyCatalog:
    def test_empty_catalog(self) -> None:
        cat = PropertyCatalog()
        assert cat.firm_type == []
        assert cat.focus == []

    def test_to_json_and_back(self) -> None:
        cat = PropertyCatalog(
            firm_type=[PropertyValue(value="hedge_fund", description="A hedge fund.")],
            focus=[PropertyValue(value="technology", description="Tech sector.")],
        )
        serialised = cat.to_json()
        restored = PropertyCatalog.from_json(serialised)
        assert len(restored.firm_type) == 1
        assert restored.firm_type[0].value == "hedge_fund"
        assert len(restored.focus) == 1
        assert restored.focus[0].value == "technology"

    def test_save_and_load(self, tmp_path: Path) -> None:
        cat = PropertyCatalog(
            firm_type=[PropertyValue(value="reit", description="A REIT.")],
            focus=[PropertyValue(value="industrial_real_estate", description="Industrial RE.")],
        )
        output_file = tmp_path / "output" / "properties.json"
        saved = cat.save(output_file)
        assert saved.exists()

        restored = PropertyCatalog.load(saved)
        assert restored.firm_type[0].value == "reit"
        assert restored.focus[0].value == "industrial_real_estate"

    def test_merge_deduplicates(self) -> None:
        cat_a = PropertyCatalog(
            firm_type=[PropertyValue(value="hedge_fund", description="A.")],
            focus=[PropertyValue(value="technology", description="Tech.")],
        )
        cat_b = PropertyCatalog(
            firm_type=[
                PropertyValue(value="hedge_fund", description="Duplicate."),
                PropertyValue(value="family_office", description="FO."),
            ],
            focus=[PropertyValue(value="healthcare", description="Health.")],
        )
        merged = cat_a.merge(cat_b)
        assert len(merged.firm_type) == 2
        # First-seen description is preserved
        assert merged.firm_type[0].description == "A."
        assert len(merged.focus) == 2


class TestPropertyCollector:
    def test_collect_returns_catalog(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        assert isinstance(catalog, PropertyCatalog)

    def test_firm_type_values_collected(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        values = {pv.value for pv in catalog.firm_type}
        assert "private_equity" in values
        assert "real_estate_developer" in values
        assert "family_office" in values

    def test_focus_values_collected(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        values = {pv.value for pv in catalog.focus}
        assert "technology" in values
        assert "healthcare" in values
        assert "commercial_real_estate" in values
        assert "diversified" in values

    def test_no_duplicates(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        firm_type_values = [pv.value for pv in catalog.firm_type]
        assert len(firm_type_values) == len(set(firm_type_values))
        focus_values = [pv.value for pv in catalog.focus]
        assert len(focus_values) == len(set(focus_values))

    def test_descriptions_provided(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        for pv in catalog.firm_type + catalog.focus:
            assert pv.description, f"Empty description for value '{pv.value}'"

    def test_known_values_have_rich_descriptions(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        pe = next(pv for pv in catalog.firm_type if pv.value == "private_equity")
        assert len(pe.description) > 50

    def test_missing_subdirectory_is_skipped(self, tmp_path: Path) -> None:
        """Collector should not raise when a configured subdirectory is absent."""
        (tmp_path / "companies").mkdir()
        (tmp_path / "companies" / "acme.md").write_text(
            "---\nname: Acme\nfirm_type: hedge_fund\nfocus: diversified\n---\n",
            encoding="utf-8",
        )
        collector = PropertyCollector(tmp_path)
        catalog = collector.collect()
        values = {pv.value for pv in catalog.firm_type}
        assert "hedge_fund" in values

    def test_sorted_output(self, tmp_kb: Path) -> None:
        collector = PropertyCollector(tmp_kb)
        catalog = collector.collect()
        firm_type_values = [pv.value for pv in catalog.firm_type]
        assert firm_type_values == sorted(firm_type_values)
        focus_values = [pv.value for pv in catalog.focus]
        assert focus_values == sorted(focus_values)

    def test_unknown_value_gets_fallback_description(self, tmp_path: Path) -> None:
        (tmp_path / "companies").mkdir()
        (tmp_path / "companies" / "weird.md").write_text(
            "---\nname: Weird Co\nfirm_type: totally_unknown_type\nfocus: outer_space\n---\n",
            encoding="utf-8",
        )
        collector = PropertyCollector(tmp_path)
        catalog = collector.collect()
        ft = next(pv for pv in catalog.firm_type if pv.value == "totally_unknown_type")
        assert "totally_unknown_type" in ft.description
