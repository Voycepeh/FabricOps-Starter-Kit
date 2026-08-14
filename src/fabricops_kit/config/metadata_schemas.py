"""Shared metadata schema contracts for FabricOps metadata tables."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

CANONICAL_METADATA_TABLES = [
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
    "METADATA_DATA_CATALOGUE",
    "METADATA_DATA_PROFILED",
    "METADATA_DATA_PROFILED_FREQUENCY",
    "METADATA_DATA_LINEAGE",
    "METADATA_DATA_ACCESS",
    "METADATA_ENRICHMENT",
    "METADATA_GUARDRAIL",
    "METADATA_GUARDRAIL_RESULTS",
    "METADATA_SOURCE_OBSERVATION",
]

AUDIT_SCHEMA_FIELDS = [
    ("_committed_by", "string", False),
    ("_committed_at", "timestamp", False),
    ("_workspace_id", "string", False),
    ("_workspace_name", "string", False),
    ("_notebook_id", "string", False),
    ("_notebook_name", "string", False),
    ("_metadata_lakehouse_name", "string", False),
    ("_activity_id", "string", False),
]



def build_metadata_schema(table_name: str, fields: list[tuple[str, str] | tuple[str, str, bool]]) -> Any:
    """Build a typed Spark StructType for a metadata table."""
    try:
        from pyspark.sql.types import BooleanType, DateType, DoubleType, IntegerType, LongType, StringType, StructField, StructType, TimestampType
    except Exception:  # pragma: no cover - local docs/tests may run without PySpark
        class _Type:
            pass

        class StringType(_Type):
            pass

        class BooleanType(_Type):
            pass

        class LongType(_Type):
            pass

        class IntegerType(_Type):
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

    logical: dict[str, list[str]] = {}
    for field in fields:
        name = field[0]
        logical.setdefault(name.lower(), []).append(name)
    duplicates = {key: values for key, values in logical.items() if len(values) > 1}
    if duplicates:
        detail = "; ".join(f"{key}: {', '.join(values)}" for key, values in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains duplicate column names: {detail}.")
    types = {
        "string": StringType(),
        "boolean": BooleanType(),
        "long": LongType(),
        "integer": IntegerType(),
        "double": DoubleType(),
        "date": DateType(),
        "timestamp": TimestampType(),
    }
    struct_fields = []
    for field in fields:
        name, kind = field[0], field[1]
        nullable = bool(field[2]) if len(field) >= 3 else True
        struct_fields.append(StructField(name, types[kind], nullable))
    return StructType(struct_fields)


def audit_schema_fields() -> list[tuple[str, str, bool]]:
    """Return the central runtime audit schema contract."""
    return list(AUDIT_SCHEMA_FIELDS)


def metadata_table_schema_registry() -> dict[str, Any]:
    """Return canonical metadata table names mapped to typed Spark schemas."""
    audit = audit_schema_fields()
    return {
        "METADATA_DATA_STEWARD": build_metadata_schema("METADATA_DATA_STEWARD", [("steward_id", "string", False), ("steward_name", "string"), ("steward_role", "string"), ("contact", "string"), ("is_active", "boolean"), ("custom_fields_json", "string"), *audit]),
        "METADATA_DATA_AGREEMENT": build_metadata_schema("METADATA_DATA_AGREEMENT", [("agreement_id", "string", False), ("agreement_version", "string", False), ("agreement_name", "string", False), ("domain", "string", False), ("provider_steward_id", "string", False), ("recipient_steward_id", "string", False), ("start_date", "date", False), ("expiry_date", "date", False), ("business_purpose", "string", False), ("supporting_documents_json", "string", True), ("approved_usage_json", "string", False), ("custom_fields_json", "string", True), *audit]),
        "METADATA_DATA_CONTRACT": build_metadata_schema("METADATA_DATA_CONTRACT", [("agreement_id", "string", False), ("metadata_table_key", "string", False), ("schema_fingerprint", "string", False), ("approved_usage_json", "string", False), *audit]),
        "METADATA_DATA_CATALOGUE": build_metadata_schema("METADATA_DATA_CATALOGUE", [("metadata_table_key", "string", False), ("metadata_column_key", "string", False), ("schema_fingerprint", "string", False), ("environment_name", "string", False), ("store_type", "string", False), ("layer", "string", False), ("schema_name", "string", True), ("table_name", "string", False), ("column_name", "string", False), ("data_type", "string", False), *audit]),
        "METADATA_DATA_PROFILED": build_metadata_schema("METADATA_DATA_PROFILED", [("metadata_table_key", "string", False), ("metadata_column_key", "string", False), ("environment_name", "string", False), ("store_type", "string", False), ("layer", "string", False), ("schema_name", "string", True), ("table_name", "string", False), ("column_name", "string", False), ("data_type", "string", False), ("row_count", "long", False), ("non_null_count", "long", False), ("null_count", "long", False), ("null_percent", "double", False), ("distinct_count", "long", False), ("distinct_percent", "double", False), ("mean_value", "double", True), ("stddev_value", "double", True), ("min_value", "string", True), ("percentile_25_value", "double", True), ("median_value", "double", True), ("percentile_75_value", "double", True), ("max_value", "string", True), ("schema_fingerprint", "string", False), ("profiled_at", "timestamp", False), *audit]),
        "METADATA_DATA_PROFILED_FREQUENCY": build_metadata_schema("METADATA_DATA_PROFILED_FREQUENCY", [("metadata_column_key", "string", False), ("value", "string", True), ("frequency_count", "long", False), ("frequency_percent", "double", False), ("frequency_rank", "integer", False), ("profiled_row_count", "long", False), ("profiled_non_null_count", "long", False), ("profiled_at", "timestamp", False), *audit]),
        "METADATA_DATA_LINEAGE": build_metadata_schema("METADATA_DATA_LINEAGE", [("lineage_event_id", "string", False), ("metadata_table_key", "string", False), ("schema_fingerprint", "string", False), ("profile_role", "string", False), ("profiled_at", "timestamp", False), ("environment_name", "string", True), *audit]),
        "METADATA_DATA_ACCESS": build_metadata_schema("METADATA_DATA_ACCESS", [("user_principal", "string"), ("role_name", "string"), ("permission", "string"), ("access_purpose", "string"), ("approval_status", "string"), ("access_scope", "string"), ("table_id", "string"), ("metadata_table_key", "string"), ("metadata_column_key", "string"), ("granted_date", "date"), ("expires_at", "timestamp"), ("approved_by", "string"), ("approved_at", "timestamp"), ("notes", "string"), *audit]),
        "METADATA_ENRICHMENT": build_metadata_schema("METADATA_ENRICHMENT", [("enrichment_id", "string", False), ("enrichment_level", "string", False), ("metadata_key", "string", False), ("enrichment_type", "string", False), ("value", "string", False), *audit]),
        "METADATA_GUARDRAIL": build_metadata_schema("METADATA_GUARDRAIL", [("guardrail_rule_id", "string"), ("configuration_version", "integer"), ("rule_key", "string"), ("rule_id", "string"), ("metadata_column_key", "string"), ("metadata_table_key", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("column_name", "string"), ("guardrail_type", "string"), ("rule_type", "string"), ("rule_parameters_json", "string"), ("severity", "string"), ("description", "string"), ("activation_state", "string"), ("is_active", "boolean"), ("review_status", "string"), ("review_state", "string"), ("created_by_role", "string"), ("author_role", "string"), ("suggestion_json", "string"), ("action_type", "string"), ("source_notebook_type", "string"), ("activation_reason", "string"), ("activated_by", "string"), ("activated_at", "timestamp"), ("superseded_by_rule_key", "string"), ("notes", "string"), ("approval_required", "boolean"), ("approval_bypassed", "boolean"), ("requires_governance_review", "boolean"), ("requires_post_review", "boolean"), ("bypass_reason", "string"), ("bypassed_by", "string"), ("bypassed_at", "timestamp"), ("governance_mode", "string"), ("approval_policy", "string"), ("submitted_by", "string"), ("submitted_at", "timestamp"), ("reviewed_by", "string"), ("reviewed_at", "timestamp"), ("review_decision", "string"), ("review_comment", "string"), ("supersedes_rule_id", "string"), ("effective_from", "date"), ("effective_to", "date"), *audit]),
        "METADATA_GUARDRAIL_RESULTS": build_metadata_schema("METADATA_GUARDRAIL_RESULTS", [("guardrail_result_id", "string", False), ("guardrail_rule_id", "string", False), ("result_id", "string", False), ("rule_key", "string", False), ("metadata_table_key", "string"), ("environment_name", "string"), ("dataset_name", "string"), ("table_name", "string"), ("column_name", "string"), ("guardrail_type", "string"), ("rule_type", "string"), ("status", "string"), ("can_continue", "boolean"), ("severity", "string"), ("reason", "string"), ("expected_value_json", "string"), ("actual_value_json", "string"), ("result_payload_json", "string"), *audit]),
        "METADATA_SOURCE_OBSERVATION": build_metadata_schema("METADATA_SOURCE_OBSERVATION", [("metadata_table_key", "string", False), ("source_target", "string", False), ("source_schema", "string", True), ("source_table", "string", False), ("partition_column", "string", False), ("partition_value", "string", False), ("change_column", "string", False), ("row_count", "long", False), ("min_change_value", "string", True), ("max_change_value", "string", True), ("is_present", "boolean", False), ("observed_at", "timestamp", False), *audit]),
    }

def _coerce_metadata_value(value: Any, type_name: str) -> Any:
    """Coerce one metadata value to the Python type expected by the setup schema."""
    if value in (None, ""):
        return None if type_name in {"TimestampType", "DateType", "BooleanType", "LongType", "DoubleType"} else ""
    if type_name == "TimestampType":
        return value if isinstance(value, datetime) else datetime.fromisoformat(str(value))
    if type_name == "DateType":
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])
    if type_name == "BooleanType":
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        return bool(value)
    if type_name == "LongType":
        return int(value)
    if type_name == "DoubleType":
        return float(value)
    return value


def coerce_metadata_row_types(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    """Return a metadata row with values aligned to the bootstrap schema types."""
    try:
        schema = metadata_table_schema_registry().get(table_name)
    except Exception:
        schema = None
    if schema is None:
        return dict(row)
    coerced = dict(row)
    for field in getattr(schema, "fields", []):
        if field.name in coerced:
            coerced[field.name] = _coerce_metadata_value(coerced[field.name], type(field.dataType).__name__)
    return coerced


def metadata_schema_type_name(data_type: Any) -> str:
    """Return the stable documentation label for a Spark metadata data type."""
    type_name = type(data_type).__name__
    stable_names = {
        "StringType": "string",
        "DateType": "date",
        "TimestampType": "timestamp",
        "BooleanType": "boolean",
        "LongType": "long",
        "DoubleType": "double",
        "IntegerType": "integer",
    }
    if type_name in stable_names:
        return stable_names[type_name]
    if hasattr(data_type, "simpleString"):
        simple = str(data_type.simpleString())
        return "long" if simple == "bigint" else simple
    text = str(data_type).lower()
    for spark_name, stable_name in stable_names.items():
        if spark_name.lower().replace("type", "") in text:
            return stable_name
    return str(data_type)


def metadata_table_schema_rows(schema: Any) -> list[dict[str, Any]]:
    """Return ordered docs-friendly schema rows from a StructType-like object."""
    return [
        {
            "name": str(field.name),
            "type": metadata_schema_type_name(getattr(field, "dataType", "")),
            "nullable": bool(getattr(field, "nullable", True)),
        }
        for field in getattr(schema, "fields", [])
    ]


def metadata_table_field_names(schema: Any) -> list[str]:
    """Return field names from a StructType-like object."""
    return list(schema.fieldNames()) if hasattr(schema, "fieldNames") else [field.name for field in schema.fields]


__all__ = [
    "AUDIT_SCHEMA_FIELDS",
    "CANONICAL_METADATA_TABLES",
    "audit_schema_fields",
    "canonical_metadata_tables",
    "coerce_metadata_row_types",
    "metadata_schema_type_name",
    "metadata_table_field_names",
    "metadata_table_schema_rows",
    "metadata_table_schema_registry",
]


def canonical_metadata_tables() -> list[str]:
    """Return the canonical FabricOps metadata table names in bootstrap order."""
    return list(CANONICAL_METADATA_TABLES)
