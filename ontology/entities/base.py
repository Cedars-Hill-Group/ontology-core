"""Base entity class for all firm ontology objects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter


class OntologyEntity:
    """Base class for a firm ontology entity backed by a Markdown file.

    Each entity is represented as a ``.md`` file whose YAML front matter
    contains structured metadata (properties) and whose body contains free-form
    prose.  Subclasses declare the *entity_type* class attribute and may add
    convenience property accessors.

    Parameters
    ----------
    path:
        Absolute or relative path to the Markdown file.

    Raises
    ------
    FileNotFoundError
        When the given path does not exist.
    """

    entity_type: str = "entity"

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).resolve()
        if not self._path.exists():
            raise FileNotFoundError(f"Entity file not found: {self._path}")
        self._post = frontmatter.load(str(self._path))

    # ------------------------------------------------------------------
    # Core accessors
    # ------------------------------------------------------------------

    @property
    def path(self) -> Path:
        """Absolute path to the source Markdown file."""
        return self._path

    @property
    def name(self) -> str:
        """Human-readable name derived from front matter or filename."""
        return str(self._post.get("name", self._path.stem))

    @property
    def metadata(self) -> dict[str, Any]:
        """All front matter key/value pairs as a plain dictionary."""
        return dict(self._post.metadata)

    @property
    def content(self) -> str:
        """Markdown body text (everything after the front matter block)."""
        return self._post.content

    def get(self, key: str, default: Any = None) -> Any:
        """Return a front matter value by *key*, or *default* if absent."""
        return self._post.get(key, default)

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------

    @classmethod
    def iter_directory(cls, directory: str | Path) -> list["OntologyEntity"]:
        """Yield entity instances for every ``.md`` file in *directory*.

        Parameters
        ----------
        directory:
            Path to the directory that contains the Markdown files.

        Returns
        -------
        list[OntologyEntity]
            Entities sorted by filename for deterministic ordering.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        entities = []
        for md_file in sorted(directory.glob("*.md")):
            try:
                entities.append(cls(md_file))
            except Exception as exc:  # noqa: BLE001
                # Skip unreadable or malformed files; emit a warning for transparency.
                import warnings

                warnings.warn(
                    f"Skipping {md_file}: {exc}",
                    stacklevel=2,
                )
                continue
        return entities

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, path={self._path!s})"

    def __str__(self) -> str:
        return self.name
