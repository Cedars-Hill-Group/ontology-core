"""
ontology-core: Cedars Hill Group firm ontology library.

Provides canonical object types, properties, and links for the firm ontology,
and utilities for collecting and publishing property values from the knowledge base.
"""

from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.project import Project

__all__ = ["Company", "Person", "Project"]
