"""Runtime documentation version helpers for FabricOps Starter Kit."""

from __future__ import annotations

import re

_DOCS_BASE_URL = "https://voycepeh.github.io/FabricOps-Starter-Kit"
_UNKNOWN_VERSION = "unknown"
_LATEST_DOCS_VERSION = "latest"


def get_package_version() -> str:
    """Return the FabricOps Starter Kit runtime package version.

    Returns
    -------
    str
        Value exposed by ``fabricops_kit.__version__``. Installed wheels read
        this from package metadata, while local source checkouts fall back to
        ``pyproject.toml``. Returns ``"unknown"`` only if the shared package
        version cannot be imported or resolved.

    Notes
    -----
    Fabric notebooks often run code from an attached custom wheel. Delegating to
    ``fabricops_kit.__version__`` keeps notebook banners, direct package version
    checks, and documentation URL helpers on the same version-detection path.
    """

    try:
        from fabricops_kit import __version__
    except Exception:
        return _UNKNOWN_VERSION
    return __version__ or _UNKNOWN_VERSION


def get_docs_version(package_version: str | None = None) -> str:
    """Return the published documentation version for a package version.

    Parameters
    ----------
    package_version : str or None, optional
        Full semantic package version such as ``"1.0.2"``. When omitted, the
        installed package version is detected with :func:`get_package_version`.

    Returns
    -------
    str
        Major/minor documentation version such as ``"1.0"``. Returns
        ``"latest"`` when the package version is missing or cannot be parsed.

    Examples
    --------
    >>> get_docs_version("1.0.2")
    '1.0'
    >>> get_docs_version("1.1.0")
    '1.1'
    """

    version = package_version if package_version is not None else get_package_version()
    if not version or version == _UNKNOWN_VERSION:
        return _LATEST_DOCS_VERSION

    match = re.match(r"^(\d+)\.(\d+)(?:\.|$)", version)
    if not match:
        return _LATEST_DOCS_VERSION
    return f"{match.group(1)}.{match.group(2)}"


def get_docs_url(package_version: str | None = None) -> str:
    """Return the documentation URL that matches a package version.

    Parameters
    ----------
    package_version : str or None, optional
        Full package version to map to a documentation version. When omitted,
        the installed package version is detected.

    Returns
    -------
    str
        Versioned documentation URL. Unknown package versions fall back to the
        ``latest`` documentation URL.
    """

    docs_version = get_docs_version(package_version)
    return f"{_DOCS_BASE_URL}/{docs_version}/"


def get_release_notes_url(package_version: str | None = None) -> str:
    """Return the release notes URL for a package version.

    Parameters
    ----------
    package_version : str or None, optional
        Full semantic package version such as ``"1.0.2"``. When omitted, the
        installed package version is detected.

    Returns
    -------
    str
        URL for the patch-specific release notes page under the latest
        published documentation. Unknown package versions fall back to the
        latest release notes index.
    """

    version = package_version if package_version is not None else get_package_version()
    if not version or version == _UNKNOWN_VERSION:
        return f"{_DOCS_BASE_URL}/{_LATEST_DOCS_VERSION}/releases/"
    return f"{_DOCS_BASE_URL}/{_LATEST_DOCS_VERSION}/releases/v{version}/"


def print_runtime_banner() -> None:
    """Print the installed package version and matching documentation links.

    Returns
    -------
    None
        This function prints a notebook-friendly runtime banner and does not
        return a value.

    Notes
    -----
    The banner is intentionally plain text so it renders consistently in
    Microsoft Fabric notebooks and local notebook previews.
    """

    package_version = get_package_version()
    docs_url = get_docs_url(package_version)
    release_notes_url = get_release_notes_url(package_version)

    print("FabricOps Starter Kit runtime")
    print(f"- Installed package version: {package_version}")
    print(f"- Documentation: {docs_url}")
    print(f"- Release notes: {release_notes_url}")
