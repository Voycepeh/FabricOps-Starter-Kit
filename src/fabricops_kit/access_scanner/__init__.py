"""Public entrypoints for independent Fabric access scanners."""

__all__ = ["scan_workspace_access", "scan_onelake_access", "scan_sql_access"]

_SCANNER_MODULES = {name: f"fabricops_kit.access_scanner.{name}" for name in __all__}


def __getattr__(name: str):
    """Lazily load implemented public access scanner callables."""
    if name not in _SCANNER_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    value = getattr(import_module(_SCANNER_MODULES[name]), name)
    globals()[name] = value
    return value
