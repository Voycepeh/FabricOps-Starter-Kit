"""Vendor-neutral, offline context for AI-assisted FabricOps tasks."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files


_SUPPORTED_TASK = "migrate_pipeline"
_SUPPORTED_SOURCE_VERSION = "0.2.0"
_RESOURCE_PACKAGE = "fabricops_kit.context.resources"


class FabricOpsContextLayer:
    """Provide self-contained FabricOps knowledge for a supported AI task.

    The Context Layer returns curated plain text and performs no network access,
    notebook mutation, or AI invocation. Resources ship in the installed Python
    package, so the result does not depend on a repository checkout.

    Notes
    -----
    The first supported task is migration of a FabricOps v0.2.0 ``02_pipeline``
    notebook to the structure and public APIs of the installed FabricOps version.
    An AI assistant should propose the adapted notebook for engineer review; this
    class does not claim that generated code is production-safe.

    Examples
    --------
    >>> from fabricops_kit import FabricOpsContextLayer
    >>> context = FabricOpsContextLayer()
    >>> prompt = context.for_task("migrate_pipeline", from_version="0.2.0")
    >>> "Environment -> Data Contract -> Read -> Transform -> Write" in prompt
    True

    """

    def for_task(self, task: str, *, from_version: str | None = None) -> str:
        """Return deterministic, self-contained context for an AI assistant.

        Parameters
        ----------
        task : str
            Supported task identifier. Currently only ``"migrate_pipeline"``.
        from_version : str, optional
            Source FabricOps version. Pipeline migration currently requires
            ``"0.2.0"``.

        Returns
        -------
        str
            Curated plain-text instructions for the requested task, including
            the source version and installed package version.

        Raises
        ------
        ValueError
            If the task is unsupported, the source version is omitted, or the
            source version has no packaged migration knowledge.

        Notes
        -----
        This method only reads resources embedded in ``fabricops-kit``. It does
        not access GitHub, documentation sites, Microsoft Fabric, or an AI API.

        Examples
        --------
        >>> FabricOpsContextLayer().for_task(
        ...     "migrate_pipeline", from_version="0.2.0"
        ... )  # doctest: +ELLIPSIS
        '...Source FabricOps version: 0.2.0...'

        """
        if task != _SUPPORTED_TASK:
            raise ValueError(f"Unsupported Context Layer task: {task!r}. Supported tasks: {_SUPPORTED_TASK!r}.")
        if from_version is None:
            raise ValueError("from_version is required for the 'migrate_pipeline' task.")
        if from_version != _SUPPORTED_SOURCE_VERSION:
            raise ValueError(
                f"Unsupported pipeline migration source version: {from_version!r}. "
                f"Supported source versions: {_SUPPORTED_SOURCE_VERSION!r}."
            )

        try:
            installed_version = version("fabricops-kit")
        except PackageNotFoundError:
            installed_version = "unknown"

        sections = [
            self._read_resource("fabricops.md"),
            self._read_resource("pipeline.md"),
            self._read_resource("migrations", f"{from_version}.md"),
        ]
        header = (
            "# FabricOps Context Layer: pipeline migration\n\n"
            f"Source FabricOps version: {from_version}\n"
            f"Target installed FabricOps version: {installed_version}\n"
        )
        return header + "\n\n" + "\n\n".join(section.strip() for section in sections) + "\n"

    @staticmethod
    def _read_resource(*parts: str) -> str:
        resource = files(_RESOURCE_PACKAGE).joinpath(*parts)
        return resource.read_text(encoding="utf-8")
