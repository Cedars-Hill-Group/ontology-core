"""Ontology catalog registry and access API."""

from __future__ import annotations

from typing import Any

from ontology.registry.loader import load_catalog_json


class CatalogRegistry:
    """Registry for accessing ontology catalogs."""

    _catalogs: dict[str, dict[str, Any]] = {}

    @classmethod
    def get_catalog(cls, name: str, version: str | None = None) -> dict[str, Any]:
        """Get a catalog by name.

        Parameters
        ----------
        name : str
            Catalog name (e.g., "attributes", "naics", "activity_cycle").
        version : str, optional
            Requested ontology version. Currently unused; for future compatibility.

        Returns
        -------
        dict[str, Any]
            The catalog data with metadata ($ontology_id, $schema_version).

        Raises
        ------
        FileNotFoundError
            When the catalog does not exist.
        """
        if name not in cls._catalogs:
            cls._catalogs[name] = load_catalog_json(name)
        return cls._catalogs[name]

    @classmethod
    def list_catalogs(cls) -> list[str]:
        """List all available catalog names.

        Returns
        -------
        list[str]
            Names of all available catalogs.
        """
        return ["attributes", "naics", "activity_cycle"]

    @classmethod
    def get_catalog_version(cls, name: str) -> str:
        """Get the schema version of a catalog.

        Parameters
        ----------
        name : str
            Catalog name.

        Returns
        -------
        str
            The catalog's schema version from $schema_version field,
            or "unknown" if not present.
        """
        catalog = cls.get_catalog(name)
        return catalog.get("$schema_version", "unknown")

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the in-memory catalog cache (for testing)."""
        cls._catalogs.clear()


# Public API
_registry = CatalogRegistry()


def get_catalog(name: str, version: str | None = None) -> dict[str, Any]:
    """Get a catalog by name.

    Parameters
    ----------
    name : str
        Catalog name (e.g., "attributes", "naics", "activity_cycle").
    version : str, optional
        Requested ontology version. Currently unused for version selection.

    Returns
    -------
    dict[str, Any]
        The catalog data including metadata.

    Raises
    ------
    FileNotFoundError
        When the catalog does not exist.
    """
    return _registry.get_catalog(name, version)


def list_catalogs() -> list[str]:
    """List all available catalogs.

    Returns
    -------
    list[str]
        Names of all available catalogs.
    """
    return _registry.list_catalogs()


def get_catalog_version(name: str) -> str:
    """Get the schema version of a catalog.

    Parameters
    ----------
    name : str
        Catalog name.

    Returns
    -------
    str
        The catalog's schema version.
    """
    return _registry.get_catalog_version(name)
