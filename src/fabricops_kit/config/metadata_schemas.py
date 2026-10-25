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
    "METADATA_PIPELINE_REGISTRY",
    "METADATA_PIPELINE_DEFINITION",
    "METADATA_PIPELINE_RUN",
    "METADATA_GUARDRAIL_RESULTS",
    "METADATA_PROCESSING_STATE",
]

# Intentional lifecycle declarations, independent of physical schema ownership.
# Historical release manifests validate this registry in test_metadata_retirements.py.
RETIRED_PREVIEW_METADATA_TABLES = {
    "METADATA_ACTIVATION_STATE": {
        "unreleased": True,
        "retired_in": "0.3.0",
        "guidance": "Authority is now in METADATA_PIPELINE_REGISTRY; drain and reconcile approvals and reservations before cutover. Never append old snapshots to the new Registry.",
    },
    "METADATA_DATA_AGREEMENT_EVIDENCE": {
        "retired_in": "0.2.0",
        "guidance": "Use exact Data Agreement and Testing references in METADATA_PIPELINE_REGISTRY where applicable.",
    },
    "METADATA_DATA_LINEAGE_TABLE": {
        "retired_in": "0.2.0",
        "guidance": "Current pipeline participation is stored in METADATA_DATA_LINEAGE.",
    },
    "METADATA_ENRICHMENT_RULES": {
        "retired_in": "0.2.0",
        "guidance": "Author descriptive Enrichment in METADATA_DATA_CONTRACT.contract_payload_json.",
    },
    "METADATA_GUARDRAIL_RULES": {
        "retired_in": "0.2.0",
        "guidance": "Author executable Guardrails in METADATA_DATA_CONTRACT.contract_payload_json.",
    },
    "METADATA_NOTEBOOK_REGISTRY": {
        "retired_in": "0.2.0",
        "guidance": "Current pipeline identities and notebook bindings use METADATA_PIPELINE_REGISTRY.",
    },
    "METADATA_PIPELINE_RUNS": {
        "retired_in": "0.2.0",
        "guidance": "Current execution history uses the typed METADATA_PIPELINE_RUN model.",
    },
    "METADATA_ENRICHMENT": {
        "retired_in": "0.3.0",
        "guidance": "Author descriptive Enrichment in METADATA_DATA_CONTRACT.contract_payload_json.",
    },
    "METADATA_GUARDRAIL": {
        "retired_in": "0.3.0",
        "guidance": "Author executable Guardrails in METADATA_DATA_CONTRACT.contract_payload_json.",
    },
    "METADATA_SOURCE_OBSERVATION": {
        "retired_in": "0.3.0",
        "guidance": "METADATA_PROCESSING_STATE is the sole runtime model; reconcile checkpoints and publication receipts before explicit migration or target rebuild/replay.",
    },
}

GOVERNANCE_METADATA_TABLES = (
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
)

ENGINEERING_METADATA_TABLES = tuple(
    table_name for table_name in CANONICAL_METADATA_TABLES if table_name not in GOVERNANCE_METADATA_TABLES
)

METADATA_TABLE_OWNERSHIP = {
    **{table_name: "governance" for table_name in GOVERNANCE_METADATA_TABLES},
    **{table_name: "engineering" for table_name in ENGINEERING_METADATA_TABLES},
}


def metadata_table_owner(table_name: str) -> str:
    """Return the authoritative writer class for a canonical metadata table."""
    try:
        return METADATA_TABLE_OWNERSHIP[table_name]
    except KeyError as exc:
        raise ValueError(f"Unknown canonical metadata table: {table_name!r}.") from exc


def metadata_table_physical_schema(config: Any, table_name: str) -> str:
    """Return the configured physical schema for a canonical metadata table."""
    owner = metadata_table_owner(table_name)
    attribute = f"{owner}_metadata_schema"
    default_schema = owner
    configured_value = config.get(attribute, default_schema) if isinstance(config, dict) else getattr(
        config, attribute, default_schema
    )
    schema_name = str(configured_value or "").strip()
    if not schema_name:
        raise ValueError(f"FrameworkConfig.{attribute} must be a non-empty schema name.")
    return schema_name

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



# Native collections share a single authority commit. None contain hidden JSON authority.
BINDING_FIELDS = [("table_id", "string", False), ("workspace_id", "string", False),
                  ("item_id", "string", False), ("kind", "string", False),
                  ("schema", "string", True), ("table_name", "string", False)]
REGISTRATION_FIELDS = [("pipeline_id", "string", False), ("environment_name", "string", False),
                       ("workspace_id", "string", False), ("notebook_id", "string", False),
                       ("notebook_name", "string", False), ("registered_at", "timestamp", False),
                       ("registered_by", "string", False), ("registration_status", "string", False), *AUDIT_SCHEMA_FIELDS]
PARTICIPANT_FIELDS = [("participant", "string", False), ("table_id", "string", False),
                      ("roles", "strings", False), ("contract_id", "string"),
                      ("contract_version", "integer"), ("payload_sha256", "string")]
APPROVAL_FIELDS = [("approval_id", "string", False), ("definition_id", "string", False),
                   ("pipeline_id", "string", False), ("environment_name", "string", False),
                   ("pipeline_name", "string", False), ("pipeline_version", "string", False),
                   ("testing_run_id", "string", False), ("testing_evidence_sha256", "string", False),
                   ("agreement_id", "string", False), ("agreement_version", "string", False),
                   ("agreement_sha256", "string", False), ("warnings", "strings", False), *AUDIT_SCHEMA_FIELDS]
OWNERSHIP_FIELDS = [("environment_name", "string", False), ("table_id", "string", False),
                    ("contract_id", "string", False), ("contract_version", "integer", False),
                    ("payload_sha256", "string", False), ("writer", "string"),
                    ("readers", "strings", False),
                    ("destination", {"struct": [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"]}, False)]
RESERVATION_FIELDS = [("environment_name", "string", False), ("reservation_id", "string", False),
                      ("pipeline_id", "string", False), ("mode", "string", False),
                      ("tables", "strings", False), ("revision", "string"),
                      ("destinations", [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"])]
CLAIM_FIELDS = [("claim_key", "string", False), ("token", "string", False), ("key", "string", False),
                ("table_id", "string", False), ("environment", "string", False),
                ("physical", {"struct": [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"]}, False),
                ("activity", "string", False), ("trigger", "string", False),
                ("expires_at", "string", False), ("execution_id", "string", False), ("completed_at", "string")]
PROFILE_EVENT_FIELDS = [("context_key", "string", False), ("activity", "string", False),
                        ("status", "string", False), ("results_persisted", "boolean"),
                        ("empty_result", "boolean"), ("profile_snapshot_id", "string"),
                        ("completed_at", "string"), ("reason", "string"), ("table_id", "string"),
                        ("row_count", "long"), ("trigger", "string"), ("environment", "string"), ("pipeline_run_id", "string"), ("executed_at", "string"),
                        ("physical", {"struct": [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"]})]


def build_metadata_schema(table_name: str, fields: list[tuple[str, Any] | tuple[str, Any, bool]]) -> Any:
    """Build a typed Spark StructType for a metadata table."""
    try:
        from pyspark.sql.types import (
            ArrayType,
            BooleanType,
            DateType,
            DoubleType,
            IntegerType,
            LongType,
            StringType,
            StructField,
            StructType,
            TimestampType,
        )
    except Exception:  # pragma: no cover - local docs/tests may run without PySpark
        class _Type:
            def simpleString(self):  # noqa: N802
                return {"LongType": "bigint", "IntegerType": "int"}.get(type(self).__name__, type(self).__name__.removesuffix("Type").lower())

        class ArrayType(_Type):
            def __init__(self, elementType, containsNull=True):  # noqa: N803
                self.elementType, self.containsNull = elementType, containsNull

            def simpleString(self):  # noqa: N802
                return "array<" + self.elementType.simpleString() + ">"

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

            def simpleString(self):  # noqa: N802
                return "struct<" + ",".join(field.name + ":" + field.dataType.simpleString() for field in self.fields) + ">"

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
        "strings": ArrayType(StringType(), False),
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
        if isinstance(kind, dict):
            data_type = build_metadata_schema(table_name + "." + name, kind["struct"])
        elif isinstance(kind, list):
            data_type = ArrayType(build_metadata_schema(table_name + "." + name, kind), False)
        else:
            data_type = types[kind]
        struct_fields.append(StructField(name, data_type, nullable))
    return StructType(struct_fields)


def audit_schema_fields() -> list[tuple[str, str, bool]]:
    """Return the central runtime audit schema contract."""
    return list(AUDIT_SCHEMA_FIELDS)


def metadata_table_schema_registry() -> dict[str, Any]:
    """Return canonical metadata table names mapped to typed Spark schemas."""
    audit = audit_schema_fields()
    return {
        "METADATA_DATA_STEWARD": build_metadata_schema(
            "METADATA_DATA_STEWARD",
            [("steward_id", "string", False), ("steward_name", "string"), ("steward_role", "string"), ("contact", "string"), ("is_active", "boolean"), ("custom_fields_json", "string"), *audit],
        ),
        "METADATA_DATA_AGREEMENT": build_metadata_schema(
            "METADATA_DATA_AGREEMENT",
            [("agreement_id", "string", False), ("agreement_version", "string", False), ("agreement_name", "string", False), ("domain", "string", False), ("provider_steward_id", "string", False), ("provider_steward_name", "string"), ("recipient_steward_id", "string", False), ("recipient_steward_name", "string"), ("start_date", "date", False), ("expiry_date", "date", False), ("business_purpose", "string", False), ("supporting_documents_json", "string", True), ("approved_usage_json", "string", False), ("custom_fields_json", "string", True), *audit],
        ),
        "METADATA_DATA_CONTRACT": build_metadata_schema(
            "METADATA_DATA_CONTRACT",
            [
                ("contract_id", "string", False),
                ("contract_version", "integer", False),
                ("table_id", "string", False),
                ("table_name", "string"),
                ("environment_name", "string", False),
                ("contract_payload_json", "string"),
                ("status", "string", False),
                *audit,
            ],
        ),
        "METADATA_DATA_CATALOGUE": build_metadata_schema(
            "METADATA_DATA_CATALOGUE",
            [
                ("metadata_level", "string"),
                ("table_id", "string"),
                ("column_id", "string"),
                ("environment_name", "string"),
                ("store_type", "string"),
                ("layer", "string"),
                ("schema_name", "string"),
                ("table_name", "string"),
                ("column_name", "string"),
                ("data_type", "string"),
                ("load_strategy", "string"),
                ("load_strategy_parameters_json", "string"),
                ("writer_workspace_id", "string"),
                ("writer_notebook_id", "string"),
                ("writer_notebook_name", "string"),
                ("scheduled_refresh_json", "string"),
                ("profile_key_candidates_json", "string"),
                ("first_profiled_at", "timestamp"),
                ("last_profiled_at", "timestamp"),
                ("is_active", "boolean"),
                *audit,
            ],
        ),
        "METADATA_DATA_PROFILED": build_metadata_schema(
            "METADATA_DATA_PROFILED",
            [
                ("profile_id", "string"),
                ("profile_snapshot_id", "string"),
                ("table_id", "string"),
                ("column_id", "string"),
                ("environment_name", "string"),
                ("data_type", "string"),
                ("table_name", "string"),
                ("column_name", "string"),
                ("row_count", "long"),
                ("non_null_count", "long"),
                ("null_count", "long"),
                ("null_percent", "double"),
                ("distinct_count", "long"),
                ("distinct_percent", "double"),
                ("mean_value", "double"),
                ("stddev_value", "double"),
                ("min_value", "string"),
                ("percentile_25_value", "double"),
                ("median_value", "double"),
                ("percentile_75_value", "double"),
                ("max_value", "string"),
                *audit,
            ],
        ),
        "METADATA_DATA_PROFILED_FREQUENCY": build_metadata_schema(
            "METADATA_DATA_PROFILED_FREQUENCY",
            [
                ("frequency_id", "string"),
                ("profile_id", "string"),
                ("profile_snapshot_id", "string"),
                ("table_id", "string"),
                ("column_id", "string"),
                ("table_name", "string"),
                ("column_name", "string"),
                ("data_type", "string"),
                ("environment_name", "string"),
                ("value", "string"),
                ("frequency_count", "long"),
                ("frequency_percent", "double"),
                ("frequency_rank", "integer"),
                ("profiled_row_count", "long"),
                ("profiled_non_null_count", "long"),
                *audit,
            ],
        ),
        "METADATA_DATA_LINEAGE": build_metadata_schema(
            "METADATA_DATA_LINEAGE",
            [
                ("lineage_id", "string"),
                ("table_id", "string"),
                ("table_name", "string"),
                ("environment_name", "string"),
                ("pipeline_role", "string"),
                *audit,
            ],
        ),
        "METADATA_DATA_ACCESS": build_metadata_schema(
            "METADATA_DATA_ACCESS",
            [
                ("access_id", "string", False),
                ("user_principal", "string", False),
                ("table_id", "string", False),
                ("table_name", "string"),
                ("environment_name", "string", False),
                ("access_level", "string", False),
                ("access_value", "string", False),
                ("access_state", "string", False),
                ("access_snapshot_id", "string", False),
                ("user_type", "string", False),
                ("role_name", "string"),
                ("permission_source", "string", False),
                ("database_name", "string", False),
                ("schema_name", "string"),
                ("object_name", "string"),
                ("object_type", "string"),
                *audit,
            ],
        ),
        "METADATA_PIPELINE_REGISTRY": build_metadata_schema(
            "METADATA_PIPELINE_REGISTRY",
            [("authority_id", "string", False), ("token", "string", False),
             ("registrations", REGISTRATION_FIELDS, False),
             ("revisions", [("environment_name", "string", False), ("revision", "string", False)], False),
             ("approvals", APPROVAL_FIELDS, False),
             ("selections", [("environment_name", "string", False), ("pipeline_id", "string", False),
                             ("approval_id", "string", False)], False),
             ("table_ownership", OWNERSHIP_FIELDS, False),
             ("reservations", RESERVATION_FIELDS, False),
             ("profiling_claims", CLAIM_FIELDS, False), *audit],
        ),
        "METADATA_PIPELINE_DEFINITION": build_metadata_schema(
            "METADATA_PIPELINE_DEFINITION",
            [("definition_id", "string", False), ("pipeline_id", "string", False),
             ("environment_name", "string", False), ("candidate_fingerprint", "string"),
             ("project_configuration_json", "string", False),
             ("participants", PARTICIPANT_FIELDS, False),
             ("operation_configurations", [("operation_key", "string", False),
                 ("configuration_sha256", "string"), ("configuration_json", "string")], False),
             ("physical_bindings", BINDING_FIELDS), *audit],
        ),
        "METADATA_PIPELINE_RUN": build_metadata_schema(
            "METADATA_PIPELINE_RUN",
            [("run_id", "string", False), ("approval_id", "string"),
             ("definition_id", "string", False), ("pipeline_id", "string", False),
             ("execution_mode", "string", False), ("environment_name", "string", False),
             ("started_at", "timestamp", False), ("completed_at", "timestamp"),
             ("status", "string", False), ("activation_revision", "string"),
             ("boundary_completed", "boolean", False),
             ("operations", [("operation_key", "string", False), ("status", "string", False),
                 ("started_at", "timestamp"), ("completed_at", "timestamp"),
                 ("stages", [("stage", "string", False), ("status", "string", False),
                             ("evaluation_status", "string")], False)], False),
             ("profiling", PROFILE_EVENT_FIELDS, False), ("warnings_json", "string", False),
             ("failures", [("code", "string", False), ("exception_type", "string")], False), *audit],
        ),
        "METADATA_GUARDRAIL_RESULTS": build_metadata_schema(
            "METADATA_GUARDRAIL_RESULTS",
            [
                ("guardrail_result_id", "string", False),
                ("guardrail_rule_id", "string", False),
                ("guardrail_version", "integer", False),
                ("table_id", "string", False),
                ("table_name", "string"),
                ("contract_id", "string", False),
                ("contract_version", "integer", False),
                ("execution_type", "string", False),
                ("run_id", "string", False),
                ("environment_name", "string", False),
                ("status", "string", False),
                ("can_continue", "boolean", False),
                ("severity", "string", False),
                ("guardrail_type", "string"),
                ("rule_id", "string"),
                ("rule_type", "string"),
                ("action", "string"),
                ("reason", "string"),
                ("result_payload_json", "string", False),
                *audit,
            ],
        ),
        "METADATA_PROCESSING_STATE": build_metadata_schema(
            "METADATA_PROCESSING_STATE",
            [
                ("record_id", "string", False),
                ("record_type", "string", False),
                ("status", "string", False),
                ("observation_id", "string"),
                ("run_id", "string"),
                ("pipeline_id", "string"),
                ("source_table_id", "string"),
                ("source_table_name", "string"),
                ("target_table_id", "string"),
                ("target_table_name", "string"),
                ("environment_name", "string", False),
                ("observed_at", "timestamp"),
                ("accepted_at", "timestamp"),
                ("partition_column", "string"),
                ("change_column", "string"),
                ("watermark_type", "string"),
                ("partition_value", "string"),
                ("row_count", "long"),
                ("min_change_value", "string"),
                ("max_change_value", "string"),
                ("content_fingerprint", "string"),
                ("is_present", "boolean"),
                ("publication_id", "string"),
                ("publication_batch_id", "string"),
                ("publication_activity_id", "string"),
                ("publication_at", "timestamp"),
                ("publication_input_rows", "long"),
                ("publication_strategy", "string"),
                *audit,
            ],
        ),
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


def _coerce_metadata_field(value, data_type):
    if value is None:
        return None
    if hasattr(data_type, "elementType"):
        return [_coerce_metadata_field(item, data_type.elementType) for item in value]
    if hasattr(data_type, "fields"):
        value = value.asDict(recursive=True) if hasattr(value, "asDict") else value
        return {field.name: _coerce_metadata_field(value.get(field.name), field.dataType) for field in data_type.fields}
    return _coerce_metadata_value(value, type(data_type).__name__)


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
            if coerced[field.name] is None and field.nullable:
                coerced[field.name] = None
            else:
                if hasattr(field.dataType, "elementType") or hasattr(field.dataType, "fields"):
                    coerced[field.name] = _coerce_metadata_field(coerced[field.name], field.dataType)
                else:
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
    "GOVERNANCE_METADATA_TABLES",
    "ENGINEERING_METADATA_TABLES",
    "METADATA_TABLE_OWNERSHIP",
    "audit_schema_fields",
    "coerce_metadata_row_types",
    "metadata_schema_type_name",
    "metadata_table_field_names",
    "metadata_table_schema_rows",
    "metadata_table_schema_registry",
    "metadata_table_owner",
    "metadata_table_physical_schema",
]
