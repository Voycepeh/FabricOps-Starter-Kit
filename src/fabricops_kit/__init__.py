"""Public notebook-friendly entrypoints for the FabricOps Starter Kit."""

import pathlib
import tomllib
from importlib.metadata import PackageNotFoundError, version

from .config import setup_notebook
from .data_agreement import get_selected_agreement, setup_data_agreement_tables, widget_render_agreement_intake_app, widget_select_agreement
from .data_lineage import build_lineage_records
from .data_profiling import profile_dataframe
from .drift import monitor_data_changes, stop_if_failed, validate_schema
from .fabric_input_output import (
    read_lakehouse_csv,
    read_lakehouse_excel,
    read_lakehouse_parquet,
    read_lakehouse_table,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from .governance_review import (
    get_selected_catalogue_table,
    load_catalogue_profile_rows,
    record_table_governance,
    setup_governance_metadata_tables,
    widget_review_table_governance,
    widget_select_catalogue_table,
)
from .handover import build_handover, render_handover_markdown
from .metadata import setup_notebook_registry_table


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
    "setup_data_agreement_tables",
    "setup_notebook_registry_table",
    "setup_governance_metadata_tables",
    "widget_render_agreement_intake_app",
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
    "monitor_data_changes",
    "stop_if_failed",
    "build_lineage_records",
    "build_handover",
    "render_handover_markdown",
    "widget_select_catalogue_table",
    "get_selected_catalogue_table",
    "load_catalogue_profile_rows",
    "widget_review_table_governance",
    "record_table_governance",
]
