"""Public notebook-friendly entrypoints for the FabricOps Starter Kit."""

import pathlib
import tomllib
from importlib.metadata import PackageNotFoundError, version

from .config import setup_metadata_tables, setup_notebook
from .data_agreement import (
    get_selected_agreement,
    widget_render_agreement_evidence,
    widget_render_data_agreement,
    widget_render_data_steward,
    widget_select_agreement,
)
from .data_profiling import profile_dataframe
from .guardrails import enforce_freshness, enforce_freshness_rule, enforce_profile_behavior, stop_if_failed, validate_schema, validate_schema_rule
from .fabric_input_output import (
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .pipeline import (
    display_guardrail_results,
    prepare_pipeline_table_configs,
    run_table_guardrails,
    write_catalogue_evidence,
    write_pipeline_lineage,
    write_pipeline_run_summary,
)
from .governance_review import (
    enforce_dq_rules,
    widget_select_guardrail_target,
    widget_enrich_table_metadata,
    widget_author_schema_freshness_profile_rules,
    widget_author_dq_rules,
    widget_author_guardrail_rules,
    widget_review_table_governance,
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
    "setup_notebook",
    "setup_metadata_tables",
    "widget_render_data_steward",
    "widget_render_data_agreement",
    "widget_render_agreement_evidence",
    "widget_select_agreement",
    "get_selected_agreement",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "write_warehouse_table",
    "profile_dataframe",
    "validate_schema",
    "validate_schema_rule",
    "enforce_freshness",
    "enforce_freshness_rule",
    "enforce_profile_behavior",
    "stop_if_failed",
    "enforce_dq_rules",
    "display_guardrail_results",
    "prepare_pipeline_table_configs",
    "run_table_guardrails",
    "write_catalogue_evidence",
    "write_pipeline_lineage",
    "write_pipeline_run_summary",
    "widget_select_guardrail_target",
    "widget_enrich_table_metadata",
    "widget_author_schema_freshness_profile_rules",
    "widget_author_dq_rules",
    "widget_author_guardrail_rules",
    "widget_review_table_governance",
    "widget_review_guardrail_governance",
]
