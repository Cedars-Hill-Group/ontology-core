"""Tests for the entity base class and concrete entity types."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ontology.entities.base import OntologyEntity
from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.project import Project


class TestOntologyEntityBase:
    def test_load_front_matter(self, tmp_path: Path) -> None:
        md = tmp_path / "test.md"
        md.write_text(
            textwrap.dedent(
                """\
                ---
                name: Test Corp
                firm_type: hedge_fund
                ---
                Body text.
                """
            ),
            encoding="utf-8",
        )
        entity = OntologyEntity(md)
        assert entity.name == "Test Corp"
        assert entity.get("firm_type") == "hedge_fund"
        assert entity.content.strip() == "Body text."

    def test_name_falls_back_to_stem(self, tmp_path: Path) -> None:
        md = tmp_path / "my-entity.md"
        md.write_text("---\n---\n", encoding="utf-8")
        entity = OntologyEntity(md)
        assert entity.name == "my-entity"

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            OntologyEntity("/nonexistent/path/entity.md")

    def test_iter_directory(self, tmp_kb: Path) -> None:
        entities = OntologyEntity.iter_directory(tmp_kb / "companies")
        assert len(entities) == 3
        names = [e.name for e in entities]
        assert "Alpha PE" in names

    def test_iter_directory_not_a_dir(self, tmp_path: Path) -> None:
        with pytest.raises(NotADirectoryError):
            OntologyEntity.iter_directory(tmp_path / "nonexistent")

    def test_metadata_dict(self, tmp_path: Path) -> None:
        md = tmp_path / "entity.md"
        md.write_text(
            "---\nname: X\nfoo: bar\n---\n",
            encoding="utf-8",
        )
        entity = OntologyEntity(md)
        assert entity.metadata["foo"] == "bar"

    def test_repr(self, tmp_path: Path) -> None:
        md = tmp_path / "entity.md"
        md.write_text("---\nname: Widget Co\n---\n", encoding="utf-8")
        entity = OntologyEntity(md)
        assert "Widget Co" in repr(entity)


class TestCompany:
    def test_firm_type_list(self, tmp_kb: Path) -> None:
        company = Company(tmp_kb / "companies" / "alpha-pe.md")
        assert company.firm_type == ["private_equity"]

    def test_focus_list_from_yaml_sequence(self, tmp_kb: Path) -> None:
        company = Company(tmp_kb / "companies" / "alpha-pe.md")
        assert company.focus == ["technology", "healthcare"]

    def test_focus_scalar_coerced_to_list(self, tmp_kb: Path) -> None:
        company = Company(tmp_kb / "companies" / "beta-cre.md")
        assert company.focus == ["commercial_real_estate"]

    def test_website(self, tmp_kb: Path) -> None:
        company = Company(tmp_kb / "companies" / "alpha-pe.md")
        assert company.website == "https://alphape.example.com"

    def test_to_dict_keys(self, tmp_kb: Path) -> None:
        company = Company(tmp_kb / "companies" / "alpha-pe.md")
        d = company.to_dict()
        assert d["entity_type"] == "company"
        assert "firm_type" in d
        assert "focus" in d

    def test_iter_directory_returns_companies(self, tmp_kb: Path) -> None:
        companies = Company.iter_directory(tmp_kb / "companies")
        assert all(isinstance(c, Company) for c in companies)
        assert len(companies) == 3

    def test_empty_firm_type_returns_empty_list(self, tmp_path: Path) -> None:
        md = tmp_path / "company.md"
        md.write_text("---\nname: No Type Co\n---\n", encoding="utf-8")
        company = Company(md)
        assert company.firm_type == []
        assert company.focus == []


class TestPerson:
    def test_person_properties(self, tmp_kb: Path) -> None:
        person = Person(tmp_kb / "people" / "jane-smith.md")
        assert person.name == "Jane Smith"
        assert person.title == "Managing Director"
        assert person.company == "Alpha PE"
        assert person.email == "jane@alphape.example.com"
        assert person.firm_type == ["private_equity"]
        assert person.focus == ["technology"]

    def test_to_dict_includes_entity_type(self, tmp_kb: Path) -> None:
        person = Person(tmp_kb / "people" / "jane-smith.md")
        d = person.to_dict()
        assert d["entity_type"] == "person"


class TestProject:
    def test_project_properties(self, tmp_kb: Path) -> None:
        project = Project(tmp_kb / "projects" / "project-x.md")
        assert project.name == "Project X"
        assert project.status == "active"
        assert project.client == "Alpha PE"
        assert project.firm_type == ["private_equity"]
        assert project.focus == ["healthcare"]

    def test_to_dict_includes_entity_type(self, tmp_kb: Path) -> None:
        project = Project(tmp_kb / "projects" / "project-x.md")
        d = project.to_dict()
        assert d["entity_type"] == "project"
