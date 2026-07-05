"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any

from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core

from .metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_field_names, metadata_table_schema_registry
from .shared import FrameworkConfig, get_store, validate_framework_config


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
    Metadata table bootstrap resolves the configured ``metadata`` FabricStore
    from ``00_env_config`` and routes reads and writes through FabricOps shared
    Lakehouse IO helpers. It does not use partial Spark table namespaces or
    require an attached default Lakehouse when the metadata target is configured.

    """
    normalized = validate_framework_config(config)
    metadata_store = get_store(config=normalized, env=env, target="metadata")
    if getattr(metadata_store, "kind", None) != "lakehouse":
        raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
    resolved_metadata_schema = (
        str(metadata_schema).strip() or None
        if metadata_schema is not None
        else (str(getattr(metadata_store, "schema", "") or "").strip() or None if getattr(metadata_store, "schema_enabled", False) else None)
    )
    context = {"config": normalized, "env": env}
    registry = metadata_table_schema_registry()
    created_tables: list[str] = []

    for table_name, schema in registry.items():
        try:
            table = read_lakehouse_table_core(table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context)
        except Exception as exc:
            message = str(exc)
            lowered = message.lower()
            is_missing = any(
                marker in lowered
                for marker in (
                    "not found",
                    "does not exist",
                    "doesn't exist",
                    "path does not exist",
                    "table_or_view_not_found",
                    "path_not_found",
                    "no such",
                )
            )
            if not is_missing:
                raise RuntimeError(
                    f"Unable to read metadata table {table_name!r}; not creating it because the error was not table-not-found. "
                    f"Original {type(exc).__name__}: {message}"
                ) from exc
            empty_frame = spark.createDataFrame([], schema=schema)
            write_lakehouse_table_core(
                empty_frame,
                table_name,
                target="metadata",
                schema=resolved_metadata_schema,
                mode="overwrite",
                options={"overwriteSchema": "true"},
                verbose=False,
                context=context,
            )
            created_tables.append(table_name)
            try:
                table = read_lakehouse_table_core(table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context)
            except Exception:
                table = None
        columns = list(getattr(table, "columns", []) or []) if table is not None else metadata_table_field_names(schema)
        missing = [field for field in metadata_table_field_names(schema) if field not in columns]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")

    try:
        steward_rows = read_lakehouse_table_core(
            "METADATA_DATA_STEWARD",
            target="metadata",
            schema=resolved_metadata_schema,
            spark_session=spark,
            context=context,
        )
        if hasattr(steward_rows, "where"):
            steward_rows = steward_rows.where("is_active = true")
        if hasattr(steward_rows, "count"):
            active_stewards = int(steward_rows.count())
        else:
            collected = steward_rows.collect() if hasattr(steward_rows, "collect") else steward_rows
            active_stewards = sum(1 for row in collected if bool((row.asDict() if hasattr(row, "asDict") else dict(row)).get("is_active")))
    except Exception:
        active_stewards = 0

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
    fully_qualified_tables = [f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in registry]
    return {
        "status": "ready" if all(status == "ready" for status in setup_statuses) else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
        "tables": list(registry),
        "metadata_schema": resolved_metadata_schema,
        "fully_qualified_tables": fully_qualified_tables,
        "created_tables": created_tables,
        "warnings": [],
        "active_metadata_tables": list(registry),
        "active_metadata_table_count": len(registry),
        "created_or_checked_tables": list(registry),
        "registration_validation": {"status": "ready", "expected_tables": list(registry), "registered_tables": list(registry), "missing_tables": [], "warnings": [], "metadata_schema": resolved_metadata_schema, "fully_qualified_tables": fully_qualified_tables},
    }


__all__ = ["setup_metadata_tables"]
