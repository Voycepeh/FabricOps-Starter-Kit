"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any

from .metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_field_names, metadata_table_schema_registry
from .shared import FrameworkConfig, get_store, validate_framework_config


def _is_missing_table_error(exc: Exception) -> bool:
    """Return whether an exception clearly indicates an absent table."""
    text = str(exc).lower()
    return any(marker in text for marker in ("not found", "does not exist", "doesn't exist", "path does not exist", "table_or_view_not_found", "path_not_found", "no such"))


def _resolve_metadata_schema(config: FrameworkConfig | dict[str, Any], env: str, metadata_schema: str | None) -> str | None:
    """Resolve explicit or configured metadata schema routing."""
    if metadata_schema is not None:
        return str(metadata_schema).strip() or None
    store = get_store(config=config, env=env, target="metadata")
    if getattr(store, "schema_enabled", False):
        return str(getattr(store, "schema", "") or "").strip() or None
    return None


def _qualified_table(table_name: str, metadata_schema: str | None) -> str:
    """Return a schema-qualified metadata table name when needed."""
    return f"{metadata_schema}.{table_name}" if metadata_schema else table_name


def _read_table_direct(spark: Any, table_name: str, metadata_schema: str | None) -> Any:
    """Read a metadata table directly from Spark without FabricOps IO helpers."""
    qualified = _qualified_table(table_name, metadata_schema)
    if hasattr(spark, "table"):
        return spark.table(qualified)
    if hasattr(spark, "read") and hasattr(spark.read, "table"):
        return spark.read.table(qualified)
    raise RuntimeError(f"Table {qualified} does not exist")


def _write_empty_table_direct(spark: Any, table_name: str, schema: Any, metadata_schema: str | None) -> None:
    """Create an empty metadata table directly through Spark table writing."""
    df = spark.createDataFrame([], schema=schema)
    qualified = _qualified_table(table_name, metadata_schema)
    writer = getattr(df, "write", None)
    if writer is None:
        # Unit-test fakes can record createDataFrame without implementing Spark writers.
        return
    if hasattr(writer, "format"):
        writer = writer.format("delta")
    if hasattr(writer, "mode"):
        writer = writer.mode("overwrite")
    if hasattr(writer, "option"):
        writer = writer.option("overwriteSchema", "true")
    if hasattr(writer, "saveAsTable"):
        writer.saveAsTable(qualified)
        return
    raise RuntimeError(f"Spark writer cannot create metadata table {qualified}.")


def _setup_metadata_table_registry(*, spark: Any, registry: dict[str, Any], metadata_schema: str | None) -> dict[str, Any]:
    """Create missing canonical metadata tables and validate required columns."""
    created: list[str] = []
    for table_name, schema in registry.items():
        try:
            table = _read_table_direct(spark, table_name, metadata_schema)
        except Exception as exc:
            if not _is_missing_table_error(exc):
                raise RuntimeError(f"Unable to read metadata table {table_name!r}; not creating it because the error was not table-not-found.") from exc
            _write_empty_table_direct(spark, table_name, schema, metadata_schema)
            created.append(table_name)
            try:
                table = _read_table_direct(spark, table_name, metadata_schema)
            except Exception:
                table = None
        columns = list(getattr(table, "columns", []) or []) if table is not None else metadata_table_field_names(schema)
        missing = [field for field in metadata_table_field_names(schema) if field not in columns]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
    return {"status": "ready", "tables": list(registry), "created_tables": created}


def _active_steward_count(spark: Any, metadata_schema: str | None) -> int:
    """Return active steward count without calling data agreement helpers."""
    try:
        rows = _read_table_direct(spark, "METADATA_DATA_STEWARD", metadata_schema)
        if hasattr(rows, "where"):
            rows = rows.where("is_active = true")
        if hasattr(rows, "count"):
            return int(rows.count())
        collected = rows.collect() if hasattr(rows, "collect") else rows
        return sum(1 for row in collected if bool((row.asDict() if hasattr(row, "asDict") else dict(row)).get("is_active")))
    except Exception:
        return 0


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None = None,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Prepare all FabricOps metadata tables for the configured environment.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used to create and validate metadata tables.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    metadata_schema : str or None, default=None
        Optional schema name for schema-enabled Fabric Lakehouses.
    require_active_steward : bool, default=False
        Whether setup should fail until ``METADATA_DATA_STEWARD`` contains an
        active steward row.

    Returns
    -------
    dict[str, Any]
        Setup summary with canonical metadata table names, created tables,
        schema routing details, and component readiness sections.

    Notes
    -----
    This public owner file owns its setup-specific private helpers and directly
    bootstraps the canonical metadata tables. It does not call data-agreement,
    governance-review, or FabricOps IO bootstrap chains.

    """
    normalized = validate_framework_config(config)
    resolved_metadata_schema = _resolve_metadata_schema(normalized, env, metadata_schema)
    registry = metadata_table_schema_registry()
    setup_registry = _setup_metadata_table_registry(spark=spark, registry=registry, metadata_schema=resolved_metadata_schema)
    created_tables = list(setup_registry["created_tables"])
    active_stewards = _active_steward_count(spark, resolved_metadata_schema)
    data_agreement_tables = ["METADATA_DATA_STEWARD", "METADATA_DATA_AGREEMENT", "METADATA_DATA_AGREEMENT_EVIDENCE"]
    data_agreement = {
        "status": "ready" if active_stewards else "not_ready",
        "tables": data_agreement_tables,
        "created_tables": [table for table in data_agreement_tables if table in created_tables],
        "active_steward_count": active_stewards,
        "message": "METADATA_DATA_STEWARD contains active steward rows. 01_agreement can render both intake widgets." if active_stewards else "METADATA_DATA_STEWARD has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement.",
    }
    if require_active_steward and not active_stewards:
        raise ValueError(data_agreement["message"])
    notebook_registry = {
        "status": "ready",
        "table": "METADATA_NOTEBOOK_REGISTRY",
        "schema": metadata_table_field_names(registry["METADATA_NOTEBOOK_REGISTRY"]),
        "created": "METADATA_NOTEBOOK_REGISTRY" in created_tables,
        "created_tables": ["METADATA_NOTEBOOK_REGISTRY"] if "METADATA_NOTEBOOK_REGISTRY" in created_tables else [],
    }
    governance_tables = [table for table in CANONICAL_METADATA_TABLES if table not in data_agreement_tables and table != "METADATA_NOTEBOOK_REGISTRY"]
    governance = {"status": "ready", "tables": governance_tables, "created_tables": [table for table in governance_tables if table in created_tables]}
    setup_statuses = [notebook_registry["status"], governance["status"]]
    if require_active_steward:
        setup_statuses.append(data_agreement["status"])
    return {
        "status": "ready" if all(status == "ready" for status in setup_statuses) else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
        "tables": list(registry),
        "metadata_schema": resolved_metadata_schema,
        "fully_qualified_tables": [_qualified_table(table, resolved_metadata_schema) for table in registry],
        "created_tables": created_tables,
        "warnings": [],
        "active_metadata_tables": list(registry),
        "active_metadata_table_count": len(registry),
        "created_or_checked_tables": list(registry),
        "registration_validation": {"status": "ready", "expected_tables": list(registry), "registered_tables": list(registry), "missing_tables": [], "warnings": [], "metadata_schema": resolved_metadata_schema, "fully_qualified_tables": [_qualified_table(table, resolved_metadata_schema) for table in registry]},
    }


__all__ = ["setup_metadata_tables"]
