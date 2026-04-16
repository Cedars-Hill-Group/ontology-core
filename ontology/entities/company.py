"""Company entity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ontology.entities.base import OntologyEntity
from ontology.entities.utils import as_list


class Company(OntologyEntity):
    """An external company or client tracked in the knowledge base.

    Expected front matter fields
    ----------------------------
    name : str
        Legal or common name of the company.
    firm_type : str | list[str]
        Category of firm (e.g. ``private_equity``, ``family_office``).
    focus : str | list[str]
        Primary industry or investment focus (e.g. ``commercial_real_estate``).
    website : str, optional
  
    """

    entity_type: str = "company"

    # ------------------------------------------------------------------
    # Convenience property accessors
    # ------------------------------------------------------------------

    @property
    def firm_type(self) -> list[str]:
        """Normalised list of firm-type tags."""
        return as_list(self.get("firm_type"))

    @property
    def focus(self) -> list[str]:
        """Normalised list of focus/industry tags."""
        return as_list(self.get("focus"))

    @property
    def website(self) -> str | None:
        """The company's website URL, if available."""
        return self.get("website")

    # ------------------------------------------------------------------
    # Class-level factory
    # ------------------------------------------------------------------

    @classmethod
    def iter_directory(cls, directory: str | Path) -> list["Company"]:  # type: ignore[override]
        """Return a list of :class:`Company` objects from a directory of ``.md`` files."""
        return super().iter_directory(directory)  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        """Serialise the company's properties to a plain dictionary."""
        return {
            "entity_type": self.entity_type,
            "name": self.name,
            "firm_type": self.firm_type,
            "focus": self.focus,
            "website": self.website,
            **{
                k: v
                for k, v in self.metadata.items()
                if k
                not in {
                    "name",
                    "firm_type",
                    "focus",
                    "website"
                }
            },
        }


