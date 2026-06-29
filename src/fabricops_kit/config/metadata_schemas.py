"""Shared metadata schema contracts for FabricOps metadata tables."""

from __future__ import annotations

from typing import Any

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


def spark_types() -> dict[str, Any]:
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
    types = spark_types()
    struct_field = types["StructField"]
    struct_type = types["StructType"]
    return struct_type([struct_field(name, types[kind], True) for name, kind in fields])


def audit_schema_fields() -> list[tuple[str, str]]:
    """Return the central runtime audit schema contract."""
    return list(AUDIT_SCHEMA_FIELDS)


def metadata_table_schema_registry() -> dict[str, Any]:
    """Return canonical metadata table names mapped to typed Spark schemas."""
    audit = audit_schema_fields()
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


def metadata_table_field_names(schema: Any) -> list[str]:
    """Return field names from a StructType-like object."""
    return list(schema.fieldNames()) if hasattr(schema, "fieldNames") else [field.name for field in schema.fields]



__all__ = [
    "AUDIT_SCHEMA_FIELDS",
    "CANONICAL_METADATA_TABLES",
    "audit_schema_fields",
    "canonical_metadata_tables",
    "metadata_table_field_names",
    "metadata_table_schema_registry",
]


def canonical_metadata_tables() -> list[str]:
    """Return the canonical FabricOps metadata table names in bootstrap order."""
    return list(CANONICAL_METADATA_TABLES)
