"""Property entity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ontology.entities.base import OntologyEntity
from ontology.entities.utils import as_list


class Property(OntologyEntity):
    """A property tracked in the knowledge base.

    Expected front matter fields
    ----------------------------
    name : str
        Property name.
    firm_type : str | list[str], optional
        Category of the client firm.
    focus : str | list[str], optional
        Primary industry or investment focus of the property.
    status : str, optional
        Lifecycle stage (e.g. ``active``, ``closed``, ``pipeline``).
    client : str, optional
        Name of the client company.
    description : str, optional
    """

    entity_type: str = "property"

    @property
    def firm_type(self) -> list[str]:
        return as_list(self.get("firm_type"))

    @property
    def focus(self) -> list[str]:
        return as_list(self.get("focus"))

    @property
    def status(self) -> str | None:
        return self.get("status")

    @property
    def client(self) -> str | None:
        return self.get("client")

    @property
    def description(self) -> str | None:
        return self.get("description")

    @classmethod
    def iter_directory(cls, directory: str | Path) -> list["Property"]:  # type: ignore[override]
        """Return a list of :class:`Property` objects from a directory of ``.md`` files."""
        return super().iter_directory(directory)  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        """Serialise the property's properties to a plain dictionary."""
        return {
            "entity_type": self.entity_type,
            "name": self.name,
            "firm_type": self.firm_type,
            "focus": self.focus,
            "status": self.status,
            "client": self.client,
            "description": self.description,
            **{
                k: v
                for k, v in self.metadata.items()
                if k
                not in {
                    "name",
                    "firm_type",
                    "focus",
                    "status",
                    "client",
                    "description",
                }
            },
        }
