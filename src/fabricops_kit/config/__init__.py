"""Supported config public contract for FabricOps notebooks."""

from __future__ import annotations

from .get_fabric_context import get_fabric_context
from .shared import (
    ConfigSmokeCheckResult,
    DataAgreementConfig,
    FabricStore,
    FrameworkConfig,
    GovernanceConfig,
    NotebookSetupContext,
    PathConfig,
)
from .setup_notebook import setup_notebook


# ---------------------------------------------------------------------------
# Metadata bootstrap public API
# ---------------------------------------------------------------------------

from typing import Any

from .shared import _validate_framework_config, get_store

_STANDARD_RUNTIME_AUDIT_COLUMNS = [
    "_committed_by", "_committed_at", "_notebook_name", "_workspace_name",
    "_metadata_lakehouse_name", "_activity_id",
]
_DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
_DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
_DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
_NOTEBOOK_REGISTRY_TABLE = "METADATA_NOTEBOOK_REGISTRY"
_CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
_ENRICHMENT_RULES_TABLE = "METADATA_ENRICHMENT_RULES"
_GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
_GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
_LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
_PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
_DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"


def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception:  # pragma: no cover - local docs/tests may run without PySpark
        class BooleanType: pass
        class DoubleType: pass
        class LongType: pass
        class StringType: pass
        class TimestampType: pass
        class StructField:
            def __init__(self, name, dataType, nullable=True):
                self.name = name; self.dataType = dataType; self.nullable = nullable
        class StructType:
            def __init__(self, fields=None): self.fields = list(fields or [])
            def fieldNames(self): return [field.name for field in self.fields]
    return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _metadata_schema_field_names(schema: Any) -> list[str]:
    """Return field names from a Spark StructType-like schema."""
    if hasattr(schema, "fieldNames"):
        return list(schema.fieldNames())
    return [field.name for field in getattr(schema, "fields", [])]


def _string_metadata_schema(table_name: str, fields: list[str]):
    """Build an explicit all-string Spark schema for lightweight metadata tables."""
    *_, StringType, StructField, StructType, _ = _spark_types()
    logical: dict[str, list[str]] = {}
    for column_name in fields:
        logical.setdefault(str(column_name).lower(), []).append(str(column_name))
    duplicates = {key: names for key, names in logical.items() if len(names) > 1}
    if duplicates:
        details = "; ".join(f"{key}: {', '.join(names)}" for key, names in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains case-insensitive duplicate column names: {details}.")
    string = StringType()
    return StructType([StructField(str(column_name), string, True) for column_name in fields])


def _typed_metadata_schema(table_name: str, fields: list[tuple[str, Any]]):
    """Build a typed Spark schema with duplicate-name validation."""
    _, _, _, _, StructField, StructType, _ = _spark_types()
    logical: dict[str, list[str]] = {}
    for name, _data_type in fields:
        logical.setdefault(str(name).lower(), []).append(str(name))
    duplicates = {key: names for key, names in logical.items() if len(names) > 1}
    if duplicates:
        details = "; ".join(f"{key}: {', '.join(names)}" for key, names in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains case-insensitive duplicate column names: {details}.")
    return StructType([StructField(name, data_type, True) for name, data_type in fields])


def _metadata_table_definitions(config: FrameworkConfig | dict[str, Any]) -> dict[str, Any]:
    """Return config-owned metadata bootstrap table definitions."""
    normalized = _validate_framework_config(config)
    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    steward_table = str(metadata_tables.get("data_steward", _DATA_STEWARD_TABLE))
    agreement_table = str(metadata_tables.get("data_agreement", _DATA_AGREEMENT_TABLE))
    evidence_table = str(metadata_tables.get("data_agreement_evidence", _DATA_AGREEMENT_EVIDENCE_TABLE))
    steward_fields = ["steward_id", "steward_name", "steward_role", "contact", "effective_from", "effective_to", "is_active", "custom_fields_json", *_STANDARD_RUNTIME_AUDIT_COLUMNS]
    agreement_fields = ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research", "custom_fields_json", *_STANDARD_RUNTIME_AUDIT_COLUMNS]
    evidence_fields = ["agreement_id", "contract_version", "evidence_type", "file_name", "file_path", "mime_type", "file_size", "uploaded_at", "uploaded_by", *_STANDARD_RUNTIME_AUDIT_COLUMNS]
    notebook_fields = ["agreement_id", "environment_name", "dataset_name", "table_name", "topic", "pipeline_name", "notebook_type", "workspace_id", "workspace_name", "notebook_id", "notebook_name", "notebook_url", "user_name", "user_id", "registered_at", "registration_id", "agreement_contract_version", "registration_role", "registration_status", "superseded_at", "superseded_by_registration_id"]
    BooleanType, DoubleType, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); long = LongType(); double = DoubleType(); boolean = BooleanType(); timestamp = TimestampType()
    audit = [(name, string) for name in ["_committed_at", "_committed_by", "_workspace_name", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]]
    definitions = {
        steward_table: _string_metadata_schema(steward_table, steward_fields),
        agreement_table: _string_metadata_schema(agreement_table, agreement_fields),
        evidence_table: _string_metadata_schema(evidence_table, evidence_fields),
        _NOTEBOOK_REGISTRY_TABLE: _string_metadata_schema(_NOTEBOOK_REGISTRY_TABLE, notebook_fields),
        _CATALOGUE_TABLE: _typed_metadata_schema(_CATALOGUE_TABLE, [("metadata_table_key", string), ("metadata_column_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string), ("profiled_at", string), ("run_timestamp", timestamp), ("evidence_role", string), ("data_type", string), ("row_count", long), ("null_count", long), ("null_percent", double), ("distinct_count", long), ("distinct_percent", double), ("min_value", string), ("max_value", string), ("distribution_type", string), ("distribution_json", string), ("profile_mode", string), ("watermark_column", string), ("watermark_value", string), ("profile_hash", string), ("profile_payload_json", string), ("governance_mode", string), ("approval_policy", string), ("bypass_allowed", boolean), ("policy_reason", string), ("policy_updated_by", string), ("policy_updated_at", string), ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), *audit]),
        _ENRICHMENT_RULES_TABLE: _typed_metadata_schema(_ENRICHMENT_RULES_TABLE, [("enrichment_rule_id", string), ("enrichment_rule_version", string), ("enrichment_rule_key", string), ("metadata_table_key", string), ("metadata_column_key", string), ("table_name", string), ("column_name", string), ("enrichment_scope", string), ("enrichment_type", string), ("enrichment_payload_json", string), ("business_name", string), ("business_description", string), ("business_meaning", string), ("column_description", string), ("classification", string), ("sensitivity_label", string), ("pii_flag", boolean), ("pii_type", string), ("data_domain", string), ("data_owner", string), ("data_steward", string), ("usage_notes", string), ("quality_notes", string), ("review_status", string), ("review_state", string), ("activation_state", string), ("is_active", boolean), ("created_by_role", string), ("source_notebook_type", string), ("source_notebook_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", string), ("requires_governance_review", boolean), ("approval_policy", string), ("governance_mode", string), ("submitted_by", string), ("submitted_at", string), ("reviewed_by", string), ("reviewed_at", string), ("review_decision", string), ("review_comment", string), ("bypass_reason", string), ("requires_post_review", boolean), ("supersedes_enrichment_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", string), ("effective_to", string), ("created_at", string), ("created_by", string), ("updated_at", string), ("updated_by", string), ("run_id", string), ("notebook_id", string), ("notebook_registry_id", string), *audit]),
        _GUARDRAIL_RULES_TABLE: _typed_metadata_schema(_GUARDRAIL_RULES_TABLE, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("activation_state", string), ("is_active", boolean), ("review_status", string), ("review_state", string), ("created_by_role", string), ("author_role", string), ("created_by", string), ("created_at", string), ("approved_by", string), ("approved_at", string), ("suggestion_json", string), ("action_type", string), ("source_notebook_type", string), ("source_notebook_id", string), ("source_workspace_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", string), ("superseded_by_rule_key", string), ("notes", string), ("approval_required", boolean), ("approval_bypassed", boolean), ("requires_governance_review", boolean), ("requires_post_review", boolean), ("bypass_reason", string), ("bypassed_by", string), ("bypassed_at", string), ("governance_mode", string), ("approval_policy", string), ("submitted_by", string), ("submitted_at", string), ("reviewed_by", string), ("reviewed_at", string), ("review_decision", string), ("review_comment", string), ("supersedes_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", string), ("effective_to", string), *audit]),
        _GUARDRAIL_RESULTS_TABLE: _typed_metadata_schema(_GUARDRAIL_RESULTS_TABLE, [("result_id", string), ("run_id", string), ("rule_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("status", string), ("can_continue", boolean), ("severity", string), ("reason", string), ("expected_value_json", string), ("actual_value_json", string), ("result_payload_json", string), ("created_at", string), *audit]),
        _LINEAGE_TABLE: _typed_metadata_schema(_LINEAGE_TABLE, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
        _PIPELINE_RUNS_TABLE: _typed_metadata_schema(_PIPELINE_RUNS_TABLE, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
        _DATA_ACCESS_TABLE: _typed_metadata_schema(_DATA_ACCESS_TABLE, [("user_principal", string), ("role_name", string), ("permission", string), ("access_purpose", string), ("approval_status", string), ("access_scope", string), ("table_id", string), ("metadata_table_key", string), ("metadata_column_key", string), ("granted_date", string), ("expires_at", string), ("approved_by", string), ("approved_at", string), ("notes", string), *audit]),
    }
    return definitions


def _metadata_table_path(config: FrameworkConfig | dict[str, Any], env: str, table_name: str, metadata_schema: str | None) -> str:
    """Return the configured Lakehouse Delta path for a metadata table."""
    store = get_store(config=config, env=env, target="metadata")
    if getattr(store, "kind", "lakehouse") != "lakehouse":
        raise ValueError("setup_metadata_tables requires the configured metadata target to be a lakehouse.")
    parts = [str(store.root).rstrip("/"), "Tables"]
    if metadata_schema:
        parts.append(str(metadata_schema).strip())
    parts.append(str(table_name).strip())
    return "/".join(parts)


def _empty_dataframe_for_schema(spark: Any, schema: Any) -> Any:
    """Create an empty Spark DataFrame for a bootstrap schema."""
    return spark.createDataFrame([], schema=schema)


def _table_exists(spark: Any, path: str) -> bool:
    """Return whether a Delta table path can be read."""
    return _existing_table_columns(spark, path) is not None


def _existing_table_columns(spark: Any, path: str) -> list[str] | None:
    """Return existing Delta table columns, or None when the path is absent."""
    try:
        table = spark.read.format("delta").load(path)
        if hasattr(table, "limit"):
            table.limit(1).collect()
    except Exception:
        return None
    return list(getattr(table, "columns", []) or [])


def _write_bootstrap_table(*, spark: Any, path: str, schema: Any, mode: str) -> None:
    """Write an empty Delta table at the target path."""
    df = _empty_dataframe_for_schema(spark, schema)
    df.write.format("delta").mode(mode).option("overwriteSchema", "true").save(path)


def _active_steward_count(spark: Any, path: str) -> int:
    """Return a best-effort count of active steward rows without agreement helpers."""
    try:
        df = spark.read.format("delta").load(path)
        if hasattr(df, "where"):
            df = df.where("is_active = true OR lower(cast(is_active as string)) = 'true'")
        if hasattr(df, "count"):
            return int(df.count())
    except Exception:
        return 0
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
        Fabric Spark session used to create and write empty Delta tables.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    metadata_schema : str or None, default=None
        Optional schema name for schema-enabled Fabric Lakehouses. Keep
        ``None`` for classic Lakehouses that store metadata tables under
        ``Tables/<table_name>``.
    require_active_steward : bool, default=False
        When True, raise if the steward registry does not contain active rows
        after bootstrap.

    Returns
    -------
    dict[str, Any]
        Setup summary with created, skipped, and overwritten table names plus
        compatibility sections for data agreement, notebook registry,
        governance, and registration validation.

    Notes
    -----
    This bootstrap utility intentionally writes directly to configured metadata
    Lakehouse Delta paths. It does not call data-agreement, governance-review,
    or generic IO helper workflows.
    """
    normalized = _validate_framework_config(config)
    resolved_schema = metadata_schema if metadata_schema is not None else (getattr(get_store(config=normalized, env=env, target="metadata"), "schema", None) if getattr(get_store(config=normalized, env=env, target="metadata"), "schema_enabled", False) else None)
    resolved_schema = str(resolved_schema).strip() if resolved_schema else None
    definitions = _metadata_table_definitions(normalized)
    created: list[str] = []
    skipped: list[str] = []
    overwritten: list[str] = []
    table_paths: dict[str, str] = {}
    for table_name, schema in definitions.items():
        path = _metadata_table_path(normalized, env, table_name, resolved_schema)
        table_paths[table_name] = path
        existing_columns = _existing_table_columns(spark, path)
        if existing_columns is not None:
            missing_columns = [field for field in _metadata_schema_field_names(schema) if field not in existing_columns]
            if missing_columns:
                raise ValueError(
                    f"{table_name} is missing required column(s): {', '.join(missing_columns)}. "
                    "Recreate or manually migrate the table before running metadata setup."
                )
            skipped.append(table_name)
            continue
        _write_bootstrap_table(spark=spark, path=path, schema=schema, mode="overwrite")
        created.append(table_name)
    steward_table = next(iter(definitions))
    steward_path = table_paths[steward_table]
    active_stewards = _active_steward_count(spark, steward_path)
    if require_active_steward and active_stewards == 0:
        raise ValueError(f"{steward_table} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement.")
    governance_tables = [_CATALOGUE_TABLE, _ENRICHMENT_RULES_TABLE, _GUARDRAIL_RULES_TABLE, _GUARDRAIL_RESULTS_TABLE, _LINEAGE_TABLE, _PIPELINE_RUNS_TABLE, _DATA_ACCESS_TABLE]
    expected_tables = list(definitions)
    fully_qualified = [f"{resolved_schema}.{table}" if resolved_schema else table for table in expected_tables]
    return {
        "status": "ready",
        "data_agreement": {
            "status": "ready" if active_stewards else "not_ready",
            "tables": [steward_table, str((normalized.data_agreement_config.metadata_tables or {}).get("data_agreement", _DATA_AGREEMENT_TABLE)), str((normalized.data_agreement_config.metadata_tables or {}).get("data_agreement_evidence", _DATA_AGREEMENT_EVIDENCE_TABLE))],
            "created_tables": [table for table in [steward_table, _DATA_AGREEMENT_TABLE, _DATA_AGREEMENT_EVIDENCE_TABLE] if table in created],
            "active_steward_count": active_stewards,
            "message": f"{steward_table} contains active steward rows." if active_stewards else f"{steward_table} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement.",
        },
        "notebook_registry": {"status": "ready", "table": _NOTEBOOK_REGISTRY_TABLE, "schema": _metadata_schema_field_names(definitions[_NOTEBOOK_REGISTRY_TABLE]) if _NOTEBOOK_REGISTRY_TABLE in definitions else [], "created": _NOTEBOOK_REGISTRY_TABLE in created, "created_tables": [_NOTEBOOK_REGISTRY_TABLE] if _NOTEBOOK_REGISTRY_TABLE in created else []},
        "governance": {"status": "ready", "tables": governance_tables, "created_tables": [table for table in governance_tables if table in created]},
        "tables": expected_tables,
        "metadata_schema": resolved_schema,
        "fully_qualified_tables": fully_qualified,
        "created_tables": created,
        "skipped_tables": skipped,
        "overwritten_tables": overwritten,
        "warnings": [],
        "active_metadata_tables": expected_tables,
        "active_metadata_table_count": len(expected_tables),
        "created_or_checked_tables": expected_tables,
        "table_paths": table_paths,
        "registration_validation": {"status": "ready", "database": get_store(config=normalized, env=env, target="metadata").name, "expected_tables": expected_tables, "expected_table_count": len(expected_tables), "registered_tables": expected_tables, "missing_tables": [], "nested_metadata_delta_paths": [], "warnings": [], "metadata_schema": resolved_schema, "fully_qualified_tables": fully_qualified, "show_tables_statement": None, "optional_documented_tables": []},
    }


__all__ = [
    "FabricStore",
    "PathConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "ConfigSmokeCheckResult",
    "NotebookSetupContext",
    "get_fabric_context",
    "setup_notebook",
    "setup_metadata_tables",
]
