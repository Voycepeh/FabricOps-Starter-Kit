"""Package-level notebook-friendly entrypoints for FabricOps Starter Kit."""

import pathlib
import tomllib
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

from .config import (
    ConfigSmokeCheckResult,
    DataAgreementConfig,
    FabricStore,
    FrameworkConfig,
    GovernanceConfig,
    NotebookSetupContext,
    PathConfig,
    setup_metadata_tables,
    setup_notebook,
)
from .io import (
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_query,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .pipeline import (
    display_guardrail_results,
    prepare_pipeline_table_configs,
    profile_and_register_dataframe,
    profile_dataframe,
    profile_frequency_distribution,
    run_table_guardrails,
    write_pipeline_run_summary,
)

CONFIG_EXPORTS = (
    "FabricStore",
    "PathConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "ConfigSmokeCheckResult",
    "NotebookSetupContext",
    "setup_notebook",
    "setup_metadata_tables",
)

IO_EXPORTS = (
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "read_warehouse_query",
    "write_warehouse_table",
)

PIPELINE_EXPORTS = (
    "profile_and_register_dataframe",
    "profile_dataframe",
    "profile_frequency_distribution",
    "display_guardrail_results",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "write_pipeline_run_summary",
)

WIDGET_EXPORTS = (
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "widget_pipeline_bootstrap",
    "widget_select_guardrail_target",
    "widget_enrich_table_metadata",
    "widget_author_schema_freshness_profile_rules",
    "widget_browse_metadata_catalogue",
    "widget_author_dq_rules",
    "widget_review_guardrail_governance",
)

_LAZY_WIDGET_MODULES = {name: f"fabricops_kit.widgets.{name}" for name in WIDGET_EXPORTS}


def __getattr__(name: str):
    """Lazily load package-root widget exports."""
    if name not in _LAZY_WIDGET_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_LAZY_WIDGET_MODULES[name])
    value = getattr(module, name)
    widgets_package = import_module("fabricops_kit.widgets")
    setattr(widgets_package, name, value)
    globals()[name] = value
    return value


def _load_package_version() -> str:
    try:
        return version("fabricops-kit")
    except PackageNotFoundError:
        pyproject_path = pathlib.Path(__file__).resolve().parents[2] / "pyproject.toml"
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
            return pyproject_data["project"]["version"]
        except (OSError, KeyError, tomllib.TOMLDecodeError):
            return "unknown"


__version__ = _load_package_version()

__all__ = [*CONFIG_EXPORTS, *IO_EXPORTS, *PIPELINE_EXPORTS, *WIDGET_EXPORTS]
