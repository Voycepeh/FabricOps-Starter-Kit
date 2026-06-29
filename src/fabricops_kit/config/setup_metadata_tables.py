"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from typing import Any

from .shared import DataAgreementConfig, FrameworkConfig, GovernanceConfig, PathConfig, STANDARD_METADATA_AUDIT_SCHEMA, get_store

METADATA_DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
METADATA_DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
METADATA_DATA_AGREEMENT_EVIDENCE_TABLE = "METADATA_DATA_AGREEMENT_EVIDENCE"
METADATA_DATA_CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
METADATA_DATA_LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
METADATA_DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
METADATA_ENRICHMENT_RULES_TABLE = "METADATA_ENRICHMENT_RULES"
METADATA_GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
METADATA_GUARDRAIL_RULES_TABLE = "METADATA_GUARDRAIL_RULES"
METADATA_NOTEBOOK_REGISTRY_TABLE = "METADATA_NOTEBOOK_REGISTRY"
METADATA_PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"


def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    import importlib
    import importlib.util

    if importlib.util.find_spec("pyspark") is not None and importlib.util.find_spec("pyspark.sql.types") is not None:
        types_module = importlib.import_module("pyspark.sql.types")
        return (
            types_module.BooleanType,
            types_module.DateType,
            types_module.DoubleType,
            types_module.LongType,
            types_module.StringType,
            types_module.StructField,
            types_module.StructType,
            types_module.TimestampType,
        )

    class _FallbackType:
        pass

    class BooleanType(_FallbackType):
        pass

    class DateType(_FallbackType):
        pass

    class DoubleType(_FallbackType):
        pass

    class LongType(_FallbackType):
        pass

    class StringType(_FallbackType):
        pass

    class TimestampType(_FallbackType):
        pass

    class StructField:
        def __init__(self, name, dataType, nullable=True):  # noqa: N803 - mirrors Spark API
            self.name = name
            self.dataType = dataType
            self.nullable = nullable

    class StructType:
        def __init__(self, fields=None):
            self.fields = list(fields or [])

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return [field.name for field in self.fields]

    return BooleanType, DateType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _schema(table_name: str, fields: list[tuple[str, Any]]):
    """Build a Spark schema with duplicate-name validation."""
    *_, StructField, StructType, _ = _spark_types()
    logical: dict[str, list[str]] = {}
    for name, _data_type in fields:
        logical.setdefault(str(name).lower(), []).append(str(name))
    duplicates = {key: names for key, names in logical.items() if len(names) > 1}
    if duplicates:
        details = "; ".join(f"{key}: {', '.join(names)}" for key, names in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains case-insensitive duplicate column names: {details}.")
    return StructType([StructField(name, data_type, True) for name, data_type in fields])


def _metadata_schema_field_names(schema: Any) -> list[str]:
    """Return field names from a Spark StructType-like schema."""
    if hasattr(schema, "fieldNames"):
        return list(schema.fieldNames())
    return [field.name for field in getattr(schema, "fields", [])]


def _validate_setup_metadata_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig:
    """Validate the minimal config contract needed for metadata bootstrap."""
    if isinstance(config, FrameworkConfig):
        normalized = config
    elif isinstance(config, dict):
        if "path_config" not in config:
            raise ValueError("Framework config is missing required keys: path_config.")
        normalized = FrameworkConfig(**config)
    else:
        raise ValueError("config must be a FrameworkConfig object or compatible mapping.")
    if not isinstance(normalized.path_config, PathConfig):
        raise ValueError("path_config must be a PathConfig object.")
    if not isinstance(normalized.governance_config, GovernanceConfig):
        raise ValueError("governance_config must be a GovernanceConfig object.")
    if not isinstance(normalized.data_agreement_config, DataAgreementConfig):
        raise ValueError("data_agreement_config must be a DataAgreementConfig object.")
    return normalized


def _resolved_metadata_table_names(config: FrameworkConfig) -> dict[str, str]:
    """Return canonical metadata table names, applying validated legacy overrides."""
    metadata_tables = config.data_agreement_config.metadata_tables or {}
    names = {
        "metadata_data_access": METADATA_DATA_ACCESS_TABLE,
        "metadata_data_agreement": str(metadata_tables.get("data_agreement", METADATA_DATA_AGREEMENT_TABLE)),
        "metadata_data_agreement_evidence": str(metadata_tables.get("data_agreement_evidence", METADATA_DATA_AGREEMENT_EVIDENCE_TABLE)),
        "metadata_data_catalogue": METADATA_DATA_CATALOGUE_TABLE,
        "metadata_data_lineage_table": METADATA_DATA_LINEAGE_TABLE,
        "metadata_data_steward": str(metadata_tables.get("data_steward", METADATA_DATA_STEWARD_TABLE)),
        "metadata_enrichment_rules": METADATA_ENRICHMENT_RULES_TABLE,
        "metadata_guardrail_results": METADATA_GUARDRAIL_RESULTS_TABLE,
        "metadata_guardrail_rules": METADATA_GUARDRAIL_RULES_TABLE,
        "metadata_notebook_registry": METADATA_NOTEBOOK_REGISTRY_TABLE,
        "metadata_pipeline_runs": METADATA_PIPELINE_RUNS_TABLE,
    }
    for logical_name, table_name in names.items():
        if not table_name or not table_name.startswith("METADATA_") or any(sep in table_name for sep in ("/", "\\", ".")):
            raise ValueError(
                f"Invalid metadata table override for {logical_name}: {table_name!r}. "
                "Use canonical METADATA_* table names unless an advanced migration requires an override."
            )
    return names


def _audit_fields(string: Any, timestamp: Any | None = None) -> list[tuple[str, Any]]:
    """Return the central runtime audit schema fields for metadata tables."""
    if timestamp is None:
        *_, TimestampType = _spark_types()
        timestamp = TimestampType()
    type_map = {"string": string, "timestamp": timestamp}
    return [(name, type_map[kind]) for name, kind in STANDARD_METADATA_AUDIT_SCHEMA]


def _metadata_data_steward_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_STEWARD."""
    BooleanType, DateType, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    date = DateType()
    boolean = BooleanType()
    timestamp = TimestampType()
    return _schema(
        table_name,
        [
            ("steward_id", string),
            ("steward_name", string),
            ("steward_role", string),
            ("contact", string),
            ("effective_from", date),
            ("effective_to", date),
            ("is_active", boolean),
            ("custom_fields_json", string),
            *_audit_fields(string, timestamp),
        ],
    )


def _metadata_data_agreement_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_AGREEMENT."""
    BooleanType, DateType, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    date = DateType()
    boolean = BooleanType()
    timestamp = TimestampType()
    return _schema(
        table_name,
        [
            ("agreement_id", string),
            ("contract_version", string),
            ("agreement_name", string),
            ("domain", string),
            ("steward_id", string),
            ("recipient", string),
            ("start_date", date),
            ("expiry_date", date),
            ("business_purpose", string),
            ("approved_usage_internal", boolean),
            ("approved_usage_external", boolean),
            ("approved_usage_research", boolean),
            ("custom_fields_json", string),
            *_audit_fields(string, timestamp),
        ],
    )


def _metadata_data_agreement_evidence_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_AGREEMENT_EVIDENCE."""
    _, _, _, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    long = LongType()
    timestamp = TimestampType()
    return _schema(
        table_name,
        [
            ("agreement_id", string),
            ("contract_version", string),
            ("evidence_type", string),
            ("file_name", string),
            ("file_path", string),
            ("mime_type", string),
            ("file_size", long),
            ("uploaded_at", timestamp),
            ("uploaded_by", string),
            *_audit_fields(string, timestamp),
        ],
    )


def _metadata_notebook_registry_schema(table_name: str):
    """Return the typed schema for METADATA_NOTEBOOK_REGISTRY."""
    _, _, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    timestamp = TimestampType()
    return _schema(
        table_name,
        [
            ("agreement_id", string),
            ("environment_name", string),
            ("dataset_name", string),
            ("table_name", string),
            ("topic", string),
            ("pipeline_name", string),
            ("notebook_type", string),
            ("workspace_id", string),
            ("workspace_name", string),
            ("notebook_id", string),
            ("notebook_name", string),
            ("notebook_url", string),
            ("user_name", string),
            ("user_id", string),
            ("registered_at", timestamp),
            ("registration_id", string),
            ("agreement_contract_version", string),
            ("registration_role", string),
            ("registration_status", string),
            ("superseded_at", timestamp),
            ("superseded_by_registration_id", string),
            *_audit_fields(string, timestamp),
        ],
    )


def _metadata_data_catalogue_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_CATALOGUE."""
    BooleanType, _, DoubleType, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); long = LongType(); double = DoubleType(); boolean = BooleanType(); timestamp = TimestampType()
    return _schema(table_name, [("metadata_table_key", string), ("metadata_column_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string), ("profiled_at", timestamp), ("run_timestamp", timestamp), ("evidence_role", string), ("data_type", string), ("row_count", long), ("null_count", long), ("null_percent", double), ("distinct_count", long), ("distinct_percent", double), ("min_value", string), ("max_value", string), ("distribution_type", string), ("distribution_json", string), ("profile_mode", string), ("watermark_column", string), ("watermark_value", string), ("profile_hash", string), ("profile_payload_json", string), ("governance_mode", string), ("approval_policy", string), ("bypass_allowed", boolean), ("policy_reason", string), ("policy_updated_by", string), ("policy_updated_at", timestamp), ("agreement_id", string), ("contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), *_audit_fields(string, timestamp)])


def _metadata_enrichment_rules_schema(table_name: str):
    """Return the typed schema for METADATA_ENRICHMENT_RULES."""
    BooleanType, DateType, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); boolean = BooleanType(); timestamp = TimestampType()
    return _schema(table_name, [("enrichment_rule_id", string), ("enrichment_rule_version", string), ("enrichment_rule_key", string), ("metadata_table_key", string), ("metadata_column_key", string), ("table_name", string), ("column_name", string), ("enrichment_scope", string), ("enrichment_type", string), ("enrichment_payload_json", string), ("business_name", string), ("business_description", string), ("business_meaning", string), ("column_description", string), ("classification", string), ("sensitivity_label", string), ("pii_flag", boolean), ("pii_type", string), ("data_domain", string), ("data_owner", string), ("data_steward", string), ("usage_notes", string), ("quality_notes", string), ("review_status", string), ("review_state", string), ("activation_state", string), ("is_active", boolean), ("created_by_role", string), ("source_notebook_type", string), ("source_notebook_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", timestamp), ("requires_governance_review", boolean), ("approval_policy", string), ("governance_mode", string), ("submitted_by", string), ("submitted_at", timestamp), ("reviewed_by", string), ("reviewed_at", timestamp), ("review_decision", string), ("review_comment", string), ("bypass_reason", string), ("requires_post_review", boolean), ("supersedes_enrichment_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", timestamp), ("effective_to", timestamp), ("created_at", timestamp), ("created_by", string), ("updated_at", timestamp), ("updated_by", string), ("run_id", string), ("notebook_id", string), ("notebook_registry_id", string), *_audit_fields(string, timestamp)])


def _metadata_guardrail_rules_schema(table_name: str):
    """Return the typed schema for METADATA_GUARDRAIL_RULES."""
    BooleanType, DateType, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); boolean = BooleanType(); timestamp = TimestampType()
    return _schema(table_name, [("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("activation_state", string), ("is_active", boolean), ("review_status", string), ("review_state", string), ("created_by_role", string), ("author_role", string), ("created_by", string), ("created_at", timestamp), ("approved_by", string), ("approved_at", timestamp), ("suggestion_json", string), ("action_type", string), ("source_notebook_type", string), ("source_notebook_id", string), ("source_workspace_id", string), ("activation_reason", string), ("activated_by", string), ("activated_at", timestamp), ("superseded_by_rule_key", string), ("notes", string), ("approval_required", boolean), ("approval_bypassed", boolean), ("requires_governance_review", boolean), ("requires_post_review", boolean), ("bypass_reason", string), ("bypassed_by", string), ("bypassed_at", timestamp), ("governance_mode", string), ("approval_policy", string), ("submitted_by", string), ("submitted_at", timestamp), ("reviewed_by", string), ("reviewed_at", timestamp), ("review_decision", string), ("review_comment", string), ("supersedes_rule_id", string), ("supersedes_record_id", string), ("superseded_by_record_id", string), ("effective_from", timestamp), ("effective_to", timestamp), *_audit_fields(string, timestamp)])


def _metadata_guardrail_results_schema(table_name: str):
    """Return the typed schema for METADATA_GUARDRAIL_RESULTS."""
    BooleanType, _, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); boolean = BooleanType(); timestamp = TimestampType()
    return _schema(table_name, [("result_id", string), ("run_id", string), ("rule_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("guardrail_type", string), ("rule_type", string), ("status", string), ("can_continue", boolean), ("severity", string), ("reason", string), ("expected_value_json", string), ("actual_value_json", string), ("result_payload_json", string), ("created_at", timestamp), *_audit_fields(string, timestamp)])


def _metadata_data_lineage_table_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_LINEAGE_TABLE."""
    _, _, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); timestamp = TimestampType()
    return _schema(table_name, [("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", timestamp), *_audit_fields(string, timestamp)])


def _metadata_pipeline_runs_schema(table_name: str):
    """Return the typed schema for METADATA_PIPELINE_RUNS."""
    _, _, _, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); long = LongType(); timestamp = TimestampType()
    return _schema(table_name, [("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", timestamp), ("completed_at", timestamp), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", timestamp), *_audit_fields(string, timestamp)])


def _metadata_data_access_schema(table_name: str):
    """Return the typed schema for METADATA_DATA_ACCESS."""
    _, DateType, _, _, StringType, _, _, TimestampType = _spark_types()
    string = StringType(); date = DateType(); timestamp = TimestampType()
    return _schema(table_name, [("user_principal", string), ("role_name", string), ("permission", string), ("access_purpose", string), ("approval_status", string), ("access_scope", string), ("table_id", string), ("metadata_table_key", string), ("metadata_column_key", string), ("granted_date", date), ("expires_at", timestamp), ("approved_by", string), ("approved_at", timestamp), ("notes", string), *_audit_fields(string, timestamp)])


def _metadata_table_definitions(config: FrameworkConfig | dict[str, Any]) -> dict[str, Any]:
    """Return canonical metadata bootstrap table definitions."""
    normalized = _validate_setup_metadata_config(config)
    names = _resolved_metadata_table_names(normalized)
    return {
        names["metadata_data_access"]: _metadata_data_access_schema(names["metadata_data_access"]),
        names["metadata_data_agreement"]: _metadata_data_agreement_schema(names["metadata_data_agreement"]),
        names["metadata_data_agreement_evidence"]: _metadata_data_agreement_evidence_schema(names["metadata_data_agreement_evidence"]),
        names["metadata_data_catalogue"]: _metadata_data_catalogue_schema(names["metadata_data_catalogue"]),
        names["metadata_data_lineage_table"]: _metadata_data_lineage_table_schema(names["metadata_data_lineage_table"]),
        names["metadata_data_steward"]: _metadata_data_steward_schema(names["metadata_data_steward"]),
        names["metadata_enrichment_rules"]: _metadata_enrichment_rules_schema(names["metadata_enrichment_rules"]),
        names["metadata_guardrail_results"]: _metadata_guardrail_results_schema(names["metadata_guardrail_results"]),
        names["metadata_guardrail_rules"]: _metadata_guardrail_rules_schema(names["metadata_guardrail_rules"]),
        names["metadata_notebook_registry"]: _metadata_notebook_registry_schema(names["metadata_notebook_registry"]),
        names["metadata_pipeline_runs"]: _metadata_pipeline_runs_schema(names["metadata_pipeline_runs"]),
    }


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


def _is_table_not_found_error(exc: Exception) -> bool:
    """Return whether an exception clearly indicates an absent Delta path/table."""
    error_class_getter = getattr(exc, "getErrorClass", None)
    try:
        error_class = str(error_class_getter() or "") if callable(error_class_getter) else ""
    except Exception:
        error_class = ""
    if error_class.upper() in {"PATH_NOT_FOUND", "TABLE_OR_VIEW_NOT_FOUND", "DELTA_TABLE_NOT_FOUND"}:
        return True
    message = str(exc).lower()
    return any(marker in message for marker in ("path does not exist", "path_not_found", "table_or_view_not_found", "delta_table_not_found", "table not found", "no such file or directory", "doesn't exist", "does not exist"))


def _existing_table_columns(spark: Any, path: str) -> list[str] | None:
    """Return existing Delta table columns, or None when the path is absent."""
    try:
        table = spark.read.format("delta").load(path)
        if hasattr(table, "limit"):
            table.limit(1).collect()
    except Exception as exc:
        if _is_table_not_found_error(exc):
            return None
        raise
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
    This bootstrap utility writes canonical METADATA_* Delta tables directly to
    the configured metadata Lakehouse path. Advanced data agreement table-name
    overrides remain supported for migration scenarios only and must still use
    valid METADATA_* table names.
    """
    normalized = _validate_setup_metadata_config(config)
    metadata_store = get_store(config=normalized, env=env, target="metadata")
    resolved_schema = metadata_schema if metadata_schema is not None else (getattr(metadata_store, "schema", None) if getattr(metadata_store, "schema_enabled", False) else None)
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
                raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing_columns)}. Recreate or manually migrate the table before running metadata setup.")
            skipped.append(table_name)
            continue
        _write_bootstrap_table(spark=spark, path=path, schema=schema, mode="overwrite")
        created.append(table_name)
    names = _resolved_metadata_table_names(normalized)
    metadata_data_steward_table = names["metadata_data_steward"]
    metadata_data_steward_path = table_paths.get(metadata_data_steward_table, next(iter(table_paths.values()), ""))
    active_stewards = _active_steward_count(spark, metadata_data_steward_path)
    if require_active_steward and active_stewards == 0:
        raise ValueError(f"{metadata_data_steward_table} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement.")
    data_agreement_tables = [
        metadata_data_steward_table,
        names["metadata_data_agreement"],
        names["metadata_data_agreement_evidence"],
    ]
    governance_tables = [
        names["metadata_data_catalogue"],
        names["metadata_enrichment_rules"],
        names["metadata_guardrail_rules"],
        names["metadata_guardrail_results"],
        names["metadata_data_lineage_table"],
        names["metadata_pipeline_runs"],
        names["metadata_data_access"],
    ]
    expected_tables = list(definitions)
    fully_qualified = [f"{resolved_schema}.{table}" if resolved_schema else table for table in expected_tables]
    return {
        "status": "ready",
        "data_agreement": {
            "status": "ready" if active_stewards else "not_ready",
            "tables": data_agreement_tables,
            "created_tables": [table for table in data_agreement_tables if table in created],
            "active_steward_count": active_stewards,
            "message": f"{metadata_data_steward_table} contains active steward rows." if active_stewards else f"{metadata_data_steward_table} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement.",
        },
        "notebook_registry": {"status": "ready", "table": names["metadata_notebook_registry"], "schema": _metadata_schema_field_names(definitions[names["metadata_notebook_registry"]]) if names["metadata_notebook_registry"] in definitions else [], "created": names["metadata_notebook_registry"] in created, "created_tables": [names["metadata_notebook_registry"]] if names["metadata_notebook_registry"] in created else []},
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
        "canonical_metadata_tables": expected_tables,
        "registration_validation": {"status": "ready", "database": metadata_store.name, "expected_tables": expected_tables, "expected_table_count": len(expected_tables), "registered_tables": expected_tables, "missing_tables": [], "nested_metadata_delta_paths": [], "warnings": [], "metadata_schema": resolved_schema, "fully_qualified_tables": fully_qualified, "show_tables_statement": None, "optional_documented_tables": []},
    }


__all__ = ["setup_metadata_tables"]
