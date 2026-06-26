"""Public notebook-friendly entrypoints for the FabricOps Starter Kit."""

import pathlib
import tomllib
from importlib.metadata import PackageNotFoundError, version

from .config import (
    ConfigSmokeCheckResult,
    DataAgreementConfig,
    FabricStore,
    FrameworkConfig,
    GovernanceConfig,
    NotebookSetupContext,
    PathConfig,
    get_fabric_context,
    setup_metadata_tables,
    setup_notebook,
)
from .data_agreement import (
    widget_render_agreement_evidence,
    widget_render_data_agreement,
    widget_render_data_steward,
)
from .data_profiling import profile_dataframe
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
    run_table_guardrails,
    start_pipeline_run,
    write_pipeline_lineage,
    write_pipeline_run_summary,
)
from .governance_review import (
    get_latest_metadata_catalogue,
    widget_select_guardrail_target,
    widget_enrich_table_metadata,
    widget_author_schema_freshness_profile_rules,
    widget_author_dq_rules,
    widget_review_guardrail_governance,
)


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

__all__ = [
    "FabricStore",
    "PathConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "ConfigSmokeCheckResult",
    "NotebookSetupContext",
    "setup_notebook",
    "setup_metadata_tables",
    "get_fabric_context",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "read_warehouse_query",
    "write_warehouse_table",
    "profile_dataframe",
    "get_latest_metadata_catalogue",
    "display_guardrail_results",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "start_pipeline_run",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_guardrail_target",
    "widget_enrich_table_metadata",
    "widget_author_schema_freshness_profile_rules",
    "widget_author_dq_rules",
    "widget_review_guardrail_governance",
]
