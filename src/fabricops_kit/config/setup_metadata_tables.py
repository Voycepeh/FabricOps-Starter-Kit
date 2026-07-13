"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any
from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core

from .metadata_schemas import CANONICAL_METADATA_TABLES, metadata_schema_type_name, metadata_table_field_names, metadata_table_schema_registry
from .shared import FrameworkConfig, get_store, validate_framework_config


def _schema_fields_by_name(schema: Any) -> dict[str, Any]:
    """Return schema fields keyed by name for Spark-like schemas."""
    return {field.name: field for field in getattr(schema, "fields", [])}


def _validate_existing_metadata_schema(table_name: str, existing_schema: Any, expected_schema: Any) -> None:
    """Validate that required metadata columns exist with compatible physical types."""
    existing = _schema_fields_by_name(existing_schema)
    expected = _schema_fields_by_name(expected_schema)
    if not existing:
        existing = {name: None for name in getattr(existing_schema, "fieldNames", lambda: [])()}
    missing = [name for name in expected if name not in existing]
    if missing:
        raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
    mismatches: list[str] = []
    for name, expected_field in expected.items():
        existing_field = existing.get(name)
        if existing_field is None:
            continue
        expected_type = metadata_schema_type_name(expected_field.dataType)
        existing_type = metadata_schema_type_name(existing_field.dataType)
        if existing_type != expected_type:
            mismatches.append(f"{name} type expected {expected_type} but found {existing_type}")
    if mismatches:
        raise ValueError(f"{table_name} physical schema does not match the canonical FabricOps metadata schema: " + "; ".join(mismatches) + ".")


def _is_missing_table_error(exc: Exception) -> bool:
    """Return whether an exception looks like a missing table/path."""
    lowered = str(exc).lower()
    return any(marker in lowered for marker in ("not found", "does not exist", "doesn't exist", "path does not exist", "table_or_view_not_found", "path_not_found", "no such"))


def _result(table_name: str, status: str, message: str, *, error_type: str | None = None) -> dict[str, Any]:
    """Return one per-table setup result."""
    item = {"table": table_name, "status": status, "message": message}
    if error_type:
        item["error_type"] = error_type
    return item


def _print_setup_summary(table_results: dict[str, dict[str, Any]], created: list[str], validated: list[str], failed: list[str]) -> None:
    """Print concise notebook-facing setup output."""
    print("FabricOps metadata table setup\n")
    for table_name, item in table_results.items():
        label = str(item["status"]).upper()
        print(f"[{label:<9}] {table_name}")
        if item["status"] == "failed":
            print(f"            {item.get('message', '')}")
    print(f"\nCreated: {len(created)}")
    print(f"Validated: {len(validated)}")
    print(f"Failed: {len(failed)}\n")
    print("Metadata setup completed successfully." if not failed else "Metadata setup completed with failures.")


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None = None,
    require_active_steward: bool = False,
    verbose: bool = True,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Prepare and validate all FabricOps metadata tables for an environment."""
    normalized = validate_framework_config(config)
    metadata_store = get_store(config=normalized, env=env, target="metadata")
    if getattr(metadata_store, "kind", None) != "lakehouse":
        raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
    resolved_metadata_schema = (str(metadata_schema).strip() or None) if metadata_schema is not None else (str(getattr(metadata_store, "schema", "") or "").strip() or None if getattr(metadata_store, "schema_enabled", False) else None)
    context = {"config": normalized, "env": env}
    registry = metadata_table_schema_registry()

    table_results: dict[str, dict[str, Any]] = {}
    created_tables: list[str] = []
    validated_tables: list[str] = []
    failed_tables: list[str] = []

    for table_name, schema in registry.items():
        try:
            created = False
            try:
                table = read_lakehouse_table_core(table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context)
            except Exception as exc:
                if not _is_missing_table_error(exc):
                    raise RuntimeError(f"Unable to read metadata table {table_name!r}. Original {type(exc).__name__}: {exc}") from exc
                empty_frame = spark.createDataFrame([], schema=schema)
                write_lakehouse_table_core(empty_frame, table_name, target="metadata", schema=resolved_metadata_schema, mode="overwrite", verbose=False, context=context)
                created = True
                table = read_lakehouse_table_core(table_name, target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context)
            if table is not None and hasattr(table, "schema"):
                _validate_existing_metadata_schema(table_name, table.schema, schema)
            else:
                columns = list(getattr(table, "columns", []) or []) if table is not None else []
                missing = [field for field in metadata_table_field_names(schema) if field not in columns]
                if missing:
                    raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
            if created:
                created_tables.append(table_name)
                table_results[table_name] = _result(table_name, "created", "Metadata table was created and validated.")
            else:
                validated_tables.append(table_name)
                table_results[table_name] = _result(table_name, "validated", "Existing metadata table schema is compatible.")
        except Exception as exc:  # continue after per-table failures
            failed_tables.append(table_name)
            table_results[table_name] = _result(table_name, "failed", f"{table_name}: {exc}", error_type=type(exc).__name__)

    try:
        steward_rows = read_lakehouse_table_core("METADATA_DATA_STEWARD", target="metadata", schema=resolved_metadata_schema, spark_session=spark, context=context)
        if hasattr(steward_rows, "where"):
            steward_rows = steward_rows.where("is_active = true")
        active_stewards = int(steward_rows.count()) if hasattr(steward_rows, "count") else 0
    except Exception:
        active_stewards = 0

    successful = created_tables + validated_tables
    status = "ready" if not failed_tables else ("partial_failure" if successful else "failed")
    data_agreement_tables = ["METADATA_DATA_STEWARD", "METADATA_DATA_AGREEMENT", "METADATA_DATA_CONTRACT"]
    data_agreement_failed = [table for table in data_agreement_tables if table in failed_tables]
    data_agreement = {"status": "failed" if data_agreement_failed else ("ready" if active_stewards else "not_ready"), "tables": data_agreement_tables, "created_tables": [table for table in data_agreement_tables if table in created_tables], "validated_tables": [table for table in data_agreement_tables if table in validated_tables], "failed_tables": data_agreement_failed, "active_steward_count": active_stewards}
    if require_active_steward and not active_stewards:
        raise ValueError("METADATA_DATA_STEWARD has no active steward rows yet.")
    governance_tables = [table for table in CANONICAL_METADATA_TABLES if table not in data_agreement_tables]
    governance_failed = [table for table in governance_tables if table in failed_tables]
    governance = {"status": "failed" if governance_failed else "ready", "tables": governance_tables, "created_tables": [table for table in governance_tables if table in created_tables], "validated_tables": [table for table in governance_tables if table in validated_tables], "failed_tables": governance_failed}
    fully_qualified_tables = [f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in registry]
    result = {"status": status, "data_agreement": data_agreement, "governance": governance, "tables": list(registry), "table_results": table_results, "metadata_schema": resolved_metadata_schema, "fully_qualified_tables": fully_qualified_tables, "created_tables": created_tables, "validated_tables": validated_tables, "failed_tables": failed_tables, "created_or_checked_tables": successful, "warnings": [], "active_metadata_tables": successful, "active_metadata_table_count": len(successful)}
    if verbose:
        _print_setup_summary(table_results, created_tables, validated_tables, failed_tables)
    if raise_on_failure and failed_tables:
        detail = "; ".join(f"{table}: {table_results[table]['message']}" for table in failed_tables)
        raise RuntimeError(f"FabricOps metadata setup failed for {len(failed_tables)} table(s): {detail}")
    return result


__all__ = ["setup_metadata_tables"]
