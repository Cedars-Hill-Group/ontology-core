"""Properties sub-package — Pydantic models and value collector."""

from ontology.properties.collector import PropertyCollector
from ontology.properties.models import PropertyValue, PropertyCatalog

__all__ = ["PropertyCollector", "PropertyValue", "PropertyCatalog"]
