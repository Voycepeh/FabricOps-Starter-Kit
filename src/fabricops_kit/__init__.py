"""Public notebook-friendly entrypoints for the FabricOps Starter Kit."""

import pathlib
import tomllib
from importlib.metadata import PackageNotFoundError, version

from .business_context import (
    draft_business_context,
    extract_column_business_context_suggestions,
    get_reviewed_business_context_rows,
    prepare_business_context_profile_input,
    widget_review_business_context,
    write_business_context,
)
from .config import setup_notebook
from .data_agreement import (
    get_selected_agreement,
    widget_render_agreement_evidence,
    widget_render_agreement_intake_app,
    widget_render_data_agreement,
    widget_render_data_steward,
    widget_select_agreement,
    setup_data_agreement_tables,
)
from .data_governance import (
    draft_governance,
    extract_governance_suggestions,
    load_governance,
    prepare_governance_input,
    widget_review_governance,
    write_governance,
)
from .data_lineage import build_lineage_handover_markdown, build_lineage_records
from .data_profiling import profile_dataframe
from .data_quality import (
    assert_dq_passed,
    draft_dq_rules,
    enforce_dq,
    get_dq_review_results,
    load_dq_rules,
    widget_review_dq_rule_deactivations,
    widget_review_dq_rules,
    validate_dq_rules,
    write_dq_rules,
)
from .drift import monitor_data_changes, stop_if_failed, validate_schema
from .fabric_input_output import (
    FabricStore,
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .handover import build_handover, render_handover_markdown
from .governance_review import (
    build_classification_records,
    build_column_context_records,
    build_dq_rule_records,
    build_profile_summary,
    catalogue_table_options,
    commit_column_classification,
    commit_column_context,
    commit_dq_rules,
    get_governance_metadata_schemas,
    get_selected_catalogue_table,
    latest_by_column,
    load_catalogue_profile_rows,
    optional_ai_generate_response,
    setup_governance_metadata_tables,
    widget_review_table_governance,
    widget_select_catalogue_table,
)
from .metadata import (
    build_runtime_audit_fields,
    current_notebook_active_registrations,
    get_notebook_registry_schema,
    load_notebook_registry,
    register_current_notebook,
    setup_notebook_registry_table,
)
from .versioning import get_docs_url, get_docs_version, get_package_version, get_release_notes_url, print_runtime_banner


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
    "widget_select_agreement",
    "get_selected_agreement",
    "register_current_notebook",
    "load_notebook_registry",
    "setup_notebook_registry_table",
    "get_notebook_registry_schema",
    "build_runtime_audit_fields",
    "current_notebook_active_registrations",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_warehouse_table",
    "write_warehouse_table",
    "profile_dataframe",
    "validate_schema",
    "monitor_data_changes",
    "stop_if_failed",
    "draft_business_context",
    "prepare_business_context_profile_input",
    "extract_column_business_context_suggestions",
    "widget_review_business_context",
    "get_reviewed_business_context_rows",
    "write_business_context",
    "draft_dq_rules",
    "widget_review_dq_rules",
    "get_dq_review_results",
    "write_dq_rules",
    "load_dq_rules",
    "enforce_dq",
    "assert_dq_passed",
    "draft_governance",
    "prepare_governance_input",
    "extract_governance_suggestions",
    "widget_review_governance",
    "write_governance",
    "load_governance",
    "build_lineage_records",
    "build_lineage_handover_markdown",
    "build_handover",
    "render_handover_markdown",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "validate_dq_rules",
    "widget_review_dq_rule_deactivations",
    "widget_render_agreement_evidence",
    "widget_render_agreement_intake_app",
    "widget_render_data_agreement",
    "widget_render_data_steward",
    "setup_data_agreement_tables",
    "FabricStore",
    "get_package_version",
    "get_docs_version",
    "get_docs_url",
    "get_release_notes_url",
    "print_runtime_banner",
    "build_classification_records",
    "build_column_context_records",
    "build_dq_rule_records",
    "build_profile_summary",
    "catalogue_table_options",
    "commit_column_classification",
    "commit_column_context",
    "commit_dq_rules",
    "get_governance_metadata_schemas",
    "get_selected_catalogue_table",
    "latest_by_column",
    "load_catalogue_profile_rows",
    "optional_ai_generate_response",
    "setup_governance_metadata_tables",
    "widget_review_table_governance",
    "widget_select_catalogue_table",
]
