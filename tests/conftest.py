"""Shared fixtures for the ontology-core test suite."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def tmp_kb(tmp_path: Path) -> Path:
    """Return a temporary knowledge-base directory with sample entity files."""
    companies = tmp_path / "companies"
    people = tmp_path / "people"
    properties = tmp_path / "properties"
    companies.mkdir()
    people.mkdir()
    properties.mkdir()

    # --- Companies ---
    (companies / "alpha-pe.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: Alpha PE
            firm_type: private_equity
            focus:
              - technology
              - healthcare
            website: https://alphape.example.com
            headquarters: New York, NY
            ---
            Alpha PE is a growth-equity firm.
            """
        ),
        encoding="utf-8",
    )

    (companies / "beta-cre.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: Beta CRE
            firm_type: real_estate_developer
            focus: commercial_real_estate
            headquarters: Dallas, TX
            ---
            Beta CRE develops office and industrial assets.
            """
        ),
        encoding="utf-8",
    )

    (companies / "gamma-fo.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: Gamma Family Office
            firm_type: family_office
            focus: diversified
            ---
            """
        ),
        encoding="utf-8",
    )

    # --- People ---
    (people / "jane-smith.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: Jane Smith
            title: Managing Director
            company: Alpha PE
            firm_type: private_equity
            focus: technology
            email: jane@alphape.example.com
            ---
            Jane leads the technology vertical.
            """
        ),
        encoding="utf-8",
    )

    # --- Properties ---
    (properties / "property-x.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: Property X
            firm_type: private_equity
            focus: healthcare
            status: active
            client: Alpha PE
            ---
            Mandated buy-side advisory for Alpha PE.
            """
        ),
        encoding="utf-8",
    )

    return tmp_path
