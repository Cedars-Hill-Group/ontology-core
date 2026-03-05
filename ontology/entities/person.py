"""Person entity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ontology.entities.base import OntologyEntity
from ontology.entities.utils import as_list


class Person(OntologyEntity):
    """An individual (contact, counterpart, or team member) in the knowledge base.

    Expected front matter fields
    ----------------------------
    name : str
        Full name.
    firm_type : str | list[str], optional
        Category of the person's firm affiliation.
    focus : str | list[str], optional
        Primary industry or investment focus.
    title : str, optional
    company : str, optional
        Name of the affiliated company.
    email : str, optional
    description : str, optional
    """

    entity_type: str = "person"

    @property
    def firm_type(self) -> list[str]:
        return as_list(self.get("firm_type"))

    @property
    def focus(self) -> list[str]:
        return as_list(self.get("focus"))

    @property
    def title(self) -> str | None:
        return self.get("title")

    @property
    def company(self) -> str | None:
        return self.get("company")

    @property
    def email(self) -> str | None:
        return self.get("email")

    @property
    def description(self) -> str | None:
        return self.get("description")

    @classmethod
    def iter_directory(cls, directory: str | Path) -> list["Person"]:  # type: ignore[override]
        """Return a list of :class:`Person` objects from a directory of ``.md`` files."""
        return super().iter_directory(directory)  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        """Serialise the person's properties to a plain dictionary."""
        return {
            "entity_type": self.entity_type,
            "name": self.name,
            "firm_type": self.firm_type,
            "focus": self.focus,
            "title": self.title,
            "company": self.company,
            "email": self.email,
            "description": self.description,
            **{
                k: v
                for k, v in self.metadata.items()
                if k
                not in {
                    "name",
                    "firm_type",
                    "focus",
                    "title",
                    "company",
                    "email",
                    "description",
                }
            },
        }


