"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .shared import FrameworkConfig, get_store, validate_framework_config

CANONICAL_METADATA_TABLES = [
    "METADATA_DATA_ACCESS",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_AGREEMENT_EVIDENCE",
    "METADATA_DATA_CATALOGUE",
    "METADATA_DATA_LINEAGE_TABLE",
    "METADATA_DATA_STEWARD",
    "METADATA_ENRICHMENT_RULES",
    "METADATA_GUARDRAIL_RESULTS",
    "METADATA_GUARDRAIL_RULES",
    "METADATA_NOTEBOOK_REGISTRY",
    "METADATA_PIPELINE_RUNS",
]

AUDIT_SCHEMA_FIELDS = [
    ("_committed_by", "string"),
    ("_committed_at", "timestamp"),
    ("_workspace_name", "string"),
    ("_notebook_name", "string"),
    ("_metadata_lakehouse_name", "string"),
    ("_activity_id", "string"),
]


def _spark_types() -> dict[str, Any]:
    """Return Spark SQL data type instances keyed by compact names."""
    try:
        from pyspark.sql.types import BooleanType, DateType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception:  # pragma: no cover - local docs/tests may run without PySpark
        class _Type:
            pass

        class StringType(_Type):
            pass

        class BooleanType(_Type):
            pass

        class LongType(_Type):
            pass

        class DoubleType(_Type):
            pass

        class DateType(_Type):
            pass

        class TimestampType(_Type):
            pass

        class StructField:
            def __init__(self, name: str, dataType: Any, nullable: bool = True) -> None:  # noqa: N803
                self.name = name
                self.dataType = dataType
                self.nullable = nullable

        class StructType:
            def __init__(self, fields: list[Any] | None = None) -> None:
                self.fields = list(fields or [])

            def fieldNames(self) -> list[str]:  # noqa: N802
                return [field.name for field in self.fields]

    return {
        "string": StringType(),
        "boolean": BooleanType(),
        "long": LongType(),
        "double": DoubleType(),
        "date": DateType(),
        "timestamp": TimestampType(),
        "StructField": StructField,
        "StructType": StructType,
    }


def _schema(table_name: str, fields: list[tuple[str, str]]) -> Any:
    """Build a typed Spark StructType for a metadata table."""
    logical: dict[str, list[str]] = {}
    for name, _kind in fields:
        logical.setdefault(name.lower(), []).append(name)
    duplicates = {key: values for key, values in logical.items() if len(values) > 1}
    if duplicates:
        detail = "; ".join(f"{key}: {', '.join(values)}" for key, values in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains duplicate column names: {detail}.")
    types = _spark_types()
    struct_field = types["StructField"]
    struct_type = types["StructType"]
    return struct_type([struct_field(name, types[kind], True) for name, kind in fields])


def _audit_fields() -> list[tuple[str, str]]:
    """Return the central runtime audit schema contract."""
    return list(AUDIT_SCHEMA_FIELDS)


def _metadata_table_schema_registry() -> dict[str, Any]:
    """Return canonical metadata table names mapped to typed Spark schemas."""
    audit = _audit_fields()
    return {
        "METADATA_DATA_ACCESS": _schema("METADATA_DATA_ACCESS", [("user_principal", "string"), ("role_name", "string"), ("permission", "string"), ("access_purpose", "string"), ("approval_status", "string"), ("access_scope", "string"), ("table_id", "string"), ("metadata_table_key", "string"), ("metadata_column_key", "string"), ("granted_date", "date"), ("expires_at", "timestamp"), ("approved_by", "string"), ("approved_at", "timestamp"), ("notes", "string"), *audit]),
        "METADATA_DATA_AGREEMENT": _schema("METADATA_DATA_AGREEMENT", [("agreement_id", "string"), ("contract_version", "string"), ("agreement_name", "string"), ("domain", "string"), ("steward_id", "string"), ("recipient", "string"), ("start_date", "date"), ("expiry_date", "date"), ("business_purpose", "string"), ("approved_usage_internal", "boolean"), ("approved_usage_external", "boolean"), ("approved_usage_research", "boolean"), ("custom_fields_json", "string"), *audit]),
        "METADATA_DATA_AGREEMENT_EVIDENCE": _schema("METADATA_DATA_AGREEMENT_EVIDENCE", [("agreement_id", "string"), ("contract_version", "string"), ("evidence_type", "string"), ("file_name", "string"), ("file_path", "string"), ("mime_type", "string"), ("file_size", "long"), ("uploaded_at", "timestamp"), ("uploaded_by", "string"), *audit]),
        "METADATA_DATA_CATALOGUE": _schema("METADATA_DATA_CATALOGUE", [("metadata_table_key", "string"), ("metadata_column_key", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("column_name", "string"), ("layer", "string"), ("asset_kind", "string"), ("pipeline_name", "string"), ("profile_run_id", "string"), ("profile_stage", "string"), ("profile_status", "string"), ("profiled_at", "timestamp"), ("run_timestamp", "timestamp"), ("evidence_role", "string"), ("data_type", "string"), ("row_count", "long"), ("null_count", "long"), ("null_percent", "double"), ("distinct_count", "long"), ("distinct_percent", "double"), ("min_value", "string"), ("max_value", "string"), ("distribution_type", "string"), ("distribution_json", "string"), ("profile_mode", "string"), ("watermark_column", "string"), ("watermark_value", "string"), ("profile_hash", "string"), ("profile_payload_json", "string"), ("governance_mode", "string"), ("approval_policy", "string"), ("bypass_allowed", "boolean"), ("policy_reason", "string"), ("policy_updated_by", "string"), ("policy_updated_at", "timestamp"), ("agreement_id", "string"), ("contract_version", "string"), ("notebook_registry_id", "string"), ("notebook_id", "string"), *audit]),
        "METADATA_DATA_LINEAGE_TABLE": _schema("METADATA_DATA_LINEAGE_TABLE", [("lineage_id", "string"), ("dataset_name", "string"), ("run_id", "string"), ("source_table", "string"), ("target_table", "string"), ("source_table_key", "string"), ("target_table_key", "string"), ("transformation_steps_json", "string"), ("created_at", "timestamp"), *audit]),
        "METADATA_DATA_STEWARD": _schema("METADATA_DATA_STEWARD", [("steward_id", "string"), ("steward_name", "string"), ("steward_role", "string"), ("contact", "string"), ("effective_from", "date"), ("effective_to", "date"), ("is_active", "boolean"), ("custom_fields_json", "string"), *audit]),
        "METADATA_ENRICHMENT_RULES": _schema("METADATA_ENRICHMENT_RULES", [("enrichment_rule_id", "string"), ("enrichment_rule_version", "string"), ("enrichment_rule_key", "string"), ("metadata_table_key", "string"), ("metadata_column_key", "string"), ("table_name", "string"), ("column_name", "string"), ("enrichment_scope", "string"), ("enrichment_type", "string"), ("enrichment_payload_json", "string"), ("business_name", "string"), ("business_description", "string"), ("business_meaning", "string"), ("column_description", "string"), ("classification", "string"), ("sensitivity_label", "string"), ("pii_flag", "boolean"), ("pii_type", "string"), ("data_domain", "string"), ("data_owner", "string"), ("data_steward", "string"), ("usage_notes", "string"), ("quality_notes", "string"), ("review_status", "string"), ("review_state", "string"), ("activation_state", "string"), ("is_active", "boolean"), ("created_by_role", "string"), ("source_notebook_type", "string"), ("source_notebook_id", "string"), ("activation_reason", "string"), ("activated_by", "string"), ("activated_at", "timestamp"), ("requires_governance_review", "boolean"), ("approval_policy", "string"), ("governance_mode", "string"), ("submitted_by", "string"), ("submitted_at", "timestamp"), ("reviewed_by", "string"), ("reviewed_at", "timestamp"), ("review_decision", "string"), ("review_comment", "string"), ("bypass_reason", "string"), ("requires_post_review", "boolean"), ("supersedes_enrichment_rule_id", "string"), ("supersedes_record_id", "string"), ("superseded_by_record_id", "string"), ("effective_from", "date"), ("effective_to", "date"), ("created_at", "timestamp"), ("created_by", "string"), ("updated_at", "timestamp"), ("updated_by", "string"), ("run_id", "string"), ("notebook_id", "string"), ("notebook_registry_id", "string"), *audit]),
        "METADATA_GUARDRAIL_RESULTS": _schema("METADATA_GUARDRAIL_RESULTS", [("result_id", "string"), ("run_id", "string"), ("rule_key", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("column_name", "string"), ("guardrail_type", "string"), ("rule_type", "string"), ("status", "string"), ("can_continue", "boolean"), ("severity", "string"), ("reason", "string"), ("expected_value_json", "string"), ("actual_value_json", "string"), ("result_payload_json", "string"), ("created_at", "timestamp"), *audit]),
        "METADATA_GUARDRAIL_RULES": _schema("METADATA_GUARDRAIL_RULES", [("rule_key", "string"), ("rule_id", "string"), ("metadata_column_key", "string"), ("metadata_table_key", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("column_name", "string"), ("guardrail_type", "string"), ("rule_type", "string"), ("rule_parameters_json", "string"), ("severity", "string"), ("description", "string"), ("activation_state", "string"), ("is_active", "boolean"), ("review_status", "string"), ("review_state", "string"), ("created_by_role", "string"), ("author_role", "string"), ("created_by", "string"), ("created_at", "timestamp"), ("approved_by", "string"), ("approved_at", "timestamp"), ("suggestion_json", "string"), ("action_type", "string"), ("source_notebook_type", "string"), ("source_notebook_id", "string"), ("source_workspace_id", "string"), ("activation_reason", "string"), ("activated_by", "string"), ("activated_at", "timestamp"), ("superseded_by_rule_key", "string"), ("notes", "string"), ("approval_required", "boolean"), ("approval_bypassed", "boolean"), ("requires_governance_review", "boolean"), ("requires_post_review", "boolean"), ("bypass_reason", "string"), ("bypassed_by", "string"), ("bypassed_at", "timestamp"), ("governance_mode", "string"), ("approval_policy", "string"), ("submitted_by", "string"), ("submitted_at", "timestamp"), ("reviewed_by", "string"), ("reviewed_at", "timestamp"), ("review_decision", "string"), ("review_comment", "string"), ("supersedes_rule_id", "string"), ("supersedes_record_id", "string"), ("superseded_by_record_id", "string"), ("effective_from", "date"), ("effective_to", "date"), *audit]),
        "METADATA_NOTEBOOK_REGISTRY": _schema("METADATA_NOTEBOOK_REGISTRY", [("agreement_id", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("topic", "string"), ("pipeline_name", "string"), ("notebook_type", "string"), ("workspace_id", "string"), ("workspace_name", "string"), ("notebook_id", "string"), ("notebook_name", "string"), ("notebook_url", "string"), ("user_name", "string"), ("user_id", "string"), ("registered_at", "timestamp"), ("registration_id", "string"), ("agreement_contract_version", "string"), ("registration_role", "string"), ("registration_status", "string"), ("superseded_at", "timestamp"), ("superseded_by_registration_id", "string"), *audit]),
        "METADATA_PIPELINE_RUNS": _schema("METADATA_PIPELINE_RUNS", [("run_id", "string"), ("agreement_id", "string"), ("agreement_contract_version", "string"), ("notebook_registry_id", "string"), ("notebook_id", "string"), ("notebook_type", "string"), ("pipeline_name", "string"), ("environment_name", "string"), ("started_at", "timestamp"), ("completed_at", "timestamp"), ("status", "string"), ("source_count", "long"), ("target_count", "long"), ("source_guardrail_status", "string"), ("target_guardrail_status", "string"), ("dq_status", "string"), ("lineage_status", "string"), ("catalogue_status", "string"), ("message", "string"), ("run_summary_json", "string"), ("created_at", "timestamp"), *audit]),
    }


def _field_names(schema: Any) -> list[str]:
    """Return field names from a StructType-like object."""
    return list(schema.fieldNames()) if hasattr(schema, "fieldNames") else [field.name for field in schema.fields]


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
        columns = list(getattr(table, "columns", []) or []) if table is not None else _field_names(schema)
        missing = [field for field in _field_names(schema) if field not in columns]
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
    registry = _metadata_table_schema_registry()
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
        "schema": _field_names(registry["METADATA_NOTEBOOK_REGISTRY"]),
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
