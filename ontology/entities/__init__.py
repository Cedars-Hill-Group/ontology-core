"""Entities sub-package."""

from ontology.entities.base import OntologyEntity
from ontology.entities.company import Company
from ontology.entities.person import Person
from ontology.entities.project import Project
from ontology.entities.utils import as_list

__all__ = ["OntologyEntity", "Company", "Person", "Project", "as_list"]
