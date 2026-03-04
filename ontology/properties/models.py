"""Pydantic models for ontology property values.

The :class:`PropertyCatalog` is the canonical JSON output that downstream
layers (data ingestion, domain services, LLM pipelines) consume.  Each entry
in a property list is a :class:`PropertyValue` that pairs the normalised
*value* with a human-readable *description* so that an LLM can choose the
correct value from the list without additional context.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PropertyValue(BaseModel):
    """A single allowed value for a categorical ontology property.

    Attributes
    ----------
    value:
        Normalised, machine-readable identifier (snake_case, lower-case).
        This is the value stored in front matter and passed between layers.
    description:
        Human-readable description of what this value means.  Used by LLMs to
        select the correct value when classifying or generating content.
    """

    value: str = Field(..., description="Normalised property value identifier.")
    description: str = Field(
        ..., description="Human-readable description for LLM consumption."
    )


class PropertyCatalog(BaseModel):
    """The full catalog of allowed values for ``firm_type`` and ``focus``.

    This is the top-level object that is serialised to JSON and consumed by
    downstream layers.  Pass the list of :class:`PropertyValue` objects for a
    given field to an LLM so that it can select the most appropriate value.

    Attributes
    ----------
    firm_type:
        Allowed values for the ``firm_type`` property.
    focus:
        Allowed values for the ``focus`` property.
    """

    firm_type: list[PropertyValue] = Field(
        default_factory=list,
        description="Allowed values for the firm_type property.",
    )
    focus: list[PropertyValue] = Field(
        default_factory=list,
        description="Allowed values for the focus property.",
    )

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_json(self, indent: int = 2) -> str:
        """Return a pretty-printed JSON string of the catalog."""
        return self.model_dump_json(indent=indent)

    def save(self, path: str | Path, indent: int = 2) -> Path:
        """Write the catalog as JSON to *path* and return the resolved path.

        Parent directories are created automatically.
        """
        output = Path(path).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.to_json(indent=indent), encoding="utf-8")
        return output

    @classmethod
    def from_json(cls, data: str | bytes) -> "PropertyCatalog":
        """Deserialise a :class:`PropertyCatalog` from a JSON string or bytes."""
        return cls.model_validate_json(data)

    @classmethod
    def load(cls, path: str | Path) -> "PropertyCatalog":
        """Load a :class:`PropertyCatalog` from a JSON file."""
        return cls.from_json(Path(path).read_bytes())

    # ------------------------------------------------------------------
    # Merge helper — useful when collecting from multiple entity types
    # ------------------------------------------------------------------

    def merge(self, other: "PropertyCatalog") -> "PropertyCatalog":
        """Return a new catalog combining *self* and *other* (no duplicates)."""
        merged_firm_type = _merge_values(self.firm_type, other.firm_type)
        merged_focus = _merge_values(self.focus, other.focus)
        return PropertyCatalog(firm_type=merged_firm_type, focus=merged_focus)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _merge_values(
    a: list[PropertyValue], b: list[PropertyValue]
) -> list[PropertyValue]:
    """Combine two value lists, preserving order and deduplicating by *value*."""
    seen: dict[str, PropertyValue] = {}
    for pv in a + b:
        if pv.value not in seen:
            seen[pv.value] = pv
    return list(seen.values())
