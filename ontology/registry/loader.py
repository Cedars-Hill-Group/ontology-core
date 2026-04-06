"""Load ontology catalog files from package data."""

from __future__ import annotations

import json
import sys
from importlib import resources
from typing import Any


def load_catalog_json(catalog_name: str) -> dict[str, Any]:
    """Load a catalog JSON file from package data.

    Parameters
    ----------
    catalog_name : str
        Name of the catalog (e.g., "attributes", "naics", "activity_cycle").

    Returns
    -------
    dict[str, Any]
        Parsed JSON content.

    Raises
    ------
    FileNotFoundError
        When the catalog file does not exist.
    """
    # Use importlib.resources to access package data
    # API differs between Python versions
    if sys.version_info >= (3, 9):
        from importlib.resources import files

        catalogs = files("ontology.catalogs")
        catalog_file = catalogs / f"{catalog_name}.json"
        try:
            content = catalog_file.read_text(encoding="utf-8")
            return json.loads(content)
        except (FileNotFoundError, AttributeError, TypeError) as exc:
            raise FileNotFoundError(
                f"Catalog '{catalog_name}' not found in ontology.catalogs"
            ) from exc
    else:
        # Python 3.8 compatibility
        try:
            from importlib.resources import read_text

            content = read_text("ontology.catalogs", f"{catalog_name}.json")
            return json.loads(content)
        except (FileNotFoundError, ModuleNotFoundError, TypeError) as exc:
            raise FileNotFoundError(
                f"Catalog '{catalog_name}' not found in ontology.catalogs"
            ) from exc
