"""Shared metadata schema contracts for FabricOps metadata tables."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

CANONICAL_METADATA_TABLES = [
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
    "METADATA_DATA_CONTRACT_ACTIVATION",
    "METADATA_DATA_CATALOGUE",
    "METADATA_DATA_PROFILED",
    "METADATA_DATA_PROFILED_FREQUENCY",
    "METADATA_DATA_LINEAGE",
    "METADATA_DATA_ACCESS",
    "METADATA_PIPELINE_ACTIVATION",
    "METADATA_PIPELINE_REGISTRY",
    "METADATA_PIPELINE_RUN",
    "METADATA_GUARDRAIL_RESULTS",
    "METADATA_PROCESSING_STATE",
]

# Explicit column retirements, never inferred from a schema difference. Values
# name a canonical replacement that must equal every non-null retired value;
# None permits removal only when the retired column is entirely SQL NULL.
# These fields are absent from current writers. Retained Run fields are excluded:
# even a duplicate field can participate in released execution content hashes.
RETIRED_METADATA_COLUMNS = {
    table: {} for table in CANONICAL_METADATA_TABLES
}
RETIRED_METADATA_COLUMNS.update({
    "METADATA_DATA_CATALOGUE": {
        "metadata_id": None, "metadata_key": None,
        "metadata_table_key": None, "metadata_column_key": None,
    },
    "METADATA_DATA_PROFILED": {
        "frequency_json": None, "profiled_at": "_committed_at",
        "metadata_table_key": None, "metadata_column_key": None,
        "store_type": None, "layer": None, "schema_name": None,
        "schema_fingerprint": None,
    },
    "METADATA_DATA_PROFILED_FREQUENCY": {
        "metadata_column_key": None, "profiled_at": "_committed_at",
    },
    "METADATA_DATA_LINEAGE": {
        "lineage_event_id": None, "profile_role": None,
        "profiled_at": "_committed_at", "recorded_at": "_committed_at",
    },
})

# Intentional lifecycle declarations, independent of physical schema ownership.
# Historical release manifests validate this registry in test_metadata_retirements.py.
RETIRED_PREVIEW_METADATA_TABLES = {
    "METADATA_DATA_AGREEMENT_EVIDENCE": {
        "retired_in": "0.2.0",
        "guidance": "METADATA_DATA_CONTRACT_ACTIVATION records exact Agreement associations; METADATA_PIPELINE_ACTIVATION records independent decisions.",
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
        "guidance": "METADATA_PROCESSING_STATE stores current source observations, checkpoints and publication receipts.",
    },
}

GOVERNANCE_METADATA_TABLES = (
    "METADATA_DATA_STEWARD",
    "METADATA_DATA_AGREEMENT",
    "METADATA_DATA_CONTRACT",
    "METADATA_DATA_CONTRACT_ACTIVATION",
    "METADATA_PIPELINE_ACTIVATION",
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
PROFILE_EVENT_FIELDS = [("context_key", "string", False), ("activity", "string", False),
                        ("status", "string", False), ("results_persisted", "boolean"),
                        ("empty_result", "boolean"), ("profile_snapshot_id", "string"),
                        ("completed_at", "string"), ("reason", "string"), ("table_id", "string"),
                        ("row_count", "long"), ("profile_scope", "string"), ("profiling_max_rows", "long"), ("trigger", "string"), ("workspace_id", "string"), ("pipeline_run_id", "string"), ("executed_at", "string"),
                        ("physical", {"struct": [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"]})]
# Dicts denote structs; tuples denote native arrays. Lists retain the existing
# array-of-struct contract used by other metadata tables.
CATALOGUE_NESTED_FIELDS = {
    "load_strategy_parameters_json": {
        "watermark_column": "string", "key_columns": ("array", "string"),
        "effective_column": "string", "tracked_columns": ("array", "string"),
    },
    "scheduled_refresh_json": {
        "status": "string", "schedules": ("array", [
            ("enabled", "boolean"), ("frequency", "string"),
            ("times", ("array", "string")), ("timezone", "string"),
        ]),
    },
    "profile_key_candidates_json": {
        "status": "string", "profile_scope": "string", "profiling_max_rows": "long", "max_combination_width": "integer", "candidates": ("array", [
            ("columns", ("array", "string")), ("column_count", "integer"),
            ("row_count", "long"), ("distinct_count", "long"),
            ("uniqueness_percent", "double"), ("null_count", "long"),
        ]),
    },
}


METADATA_JSON_COLUMNS = {
    "METADATA_DATA_CATALOGUE": tuple(CATALOGUE_NESTED_FIELDS),
    "METADATA_PIPELINE_RUN": ("operations", "profiling", "failures"),
}


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
            data_type = build_metadata_schema(table_name + "." + name, kind["struct"] if "struct" in kind else list(kind.items()))
        elif isinstance(kind, list):
            data_type = ArrayType(build_metadata_schema(table_name + "." + name, kind), False)
        elif isinstance(kind, tuple) and kind[0] == "array":
            element = build_metadata_schema(table_name + "." + name, kind[1]) if isinstance(kind[1], list) else types[kind[1]]
            data_type = ArrayType(element, True)
        else:
            data_type = types[kind]
        struct_fields.append(StructField(name, data_type, nullable))
    return StructType(struct_fields)


def audit_schema_fields() -> list[tuple[str, str, bool]]:
    """Return the central runtime audit schema contract."""
    return list(AUDIT_SCHEMA_FIELDS)


def metadata_table_schema_registry(*, logical: bool = False) -> dict[str, Any]:
    """Return physical schemas, or typed logical contracts for JSON metadata."""
    audit = audit_schema_fields()
    schemas = {
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
                ("table_id", "string"),
                ("source_id", "string"),
                ("table_name", "string"),
                ("evidence_workspace_id", "string", False),
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
                ("workspace_id", "string"),
                ("store_type", "string"),
                ("layer", "string"),
                ("schema_name", "string"),
                ("table_name", "string"),
                ("column_name", "string"),
                ("data_type", "string"),
                ("load_strategy", "string"),
                ("load_strategy_parameters_json", CATALOGUE_NESTED_FIELDS["load_strategy_parameters_json"]),
                ("writer_workspace_id", "string"),
                ("writer_notebook_id", "string"),
                ("writer_notebook_name", "string"),
                ("scheduled_refresh_json", CATALOGUE_NESTED_FIELDS["scheduled_refresh_json"]),
                ("profile_key_candidates_json", CATALOGUE_NESTED_FIELDS["profile_key_candidates_json"]),
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
                ("workspace_id", "string"),
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
                ("profile_scope", "string"),
                ("profiling_max_rows", "long"),
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
                ("workspace_id", "string"),
                ("value", "string"),
                ("frequency_count", "long"),
                ("frequency_percent", "double"),
                ("frequency_rank", "integer"),
                ("profiled_row_count", "long"),
                ("profiled_non_null_count", "long"),
                ("profile_scope", "string"),
                ("profiling_max_rows", "long"),
                *audit,
            ],
        ),
        "METADATA_DATA_LINEAGE": build_metadata_schema(
            "METADATA_DATA_LINEAGE",
            [
                ("lineage_id", "string"),
                ("table_id", "string"),
                ("table_name", "string"),
                ("workspace_id", "string"),
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
                ("workspace_id", "string", False),
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
        "METADATA_DATA_CONTRACT_ACTIVATION": build_metadata_schema(
            "METADATA_DATA_CONTRACT_ACTIVATION",
            [("workspace_id", "string", False), ("table_id", "string"), ("source_id", "string"),
             ("contract_id", "string", False), ("contract_version", "integer", False),
             ("payload_sha256", "string", False), ("activation_id", "string", False),
             ("revision", "integer", False), ("status", "string", False),
             ("destination_json", "string", False),
             ("activated_at", "timestamp", False),
             ("agreement_id", "string"), ("agreement_version", "string"), ("agreement_sha256", "string"), *audit],
        ),
        "METADATA_PIPELINE_ACTIVATION": build_metadata_schema(
            "METADATA_PIPELINE_ACTIVATION",
            [("approval_id", "string", False), ("submission_id", "string", False),
             ("submission_sha256", "string", False), ("execution_workspace_id", "string", False),
             ("pipeline_id", "string", False), ("revision", "integer", False),
             ("status", "string", False), ("decision_kind", "string", False),
             ("package_json", "string", False), ("policy_json", "string", False),
             ("expected_active_version", "integer"), ("restores_promotion_id", "string"),
             ("expires_at", "timestamp"),
             ("decided_at", "timestamp", False), ("review_note", "string", False), *audit],
        ),
        "METADATA_PIPELINE_REGISTRY": build_metadata_schema(
            "METADATA_PIPELINE_REGISTRY",
            [("execution_workspace_id", "string", False), ("pipeline_id", "string", False),
             ("pipeline_version", "integer", False), ("promotion_id", "string", False),
             ("status", "string", False), ("source_workspace_id", "string", False),
             ("source_notebook_id", "string", False), ("governed_notebook_id", "string", False),
             ("snapshot_uri", "string", False), ("snapshot_sha256", "string", False),
             ("source_snapshot_uri", "string", False), ("source_snapshot_sha256", "string", False),
             ("executable_sha256", "string", False), ("operations_json", "string", False),
             ("bindings_sha256", "string", False), ("parameters_json", "string", False),
             ("approval_id", "string", False), ("submission_id", "string", False),
             ("submission_sha256", "string", False), ("restored_from_version", "integer"),
             ("promoted_at", "timestamp", False), *audit],
        ),
        "METADATA_PIPELINE_RUN": build_metadata_schema(
            "METADATA_PIPELINE_RUN",
            [("run_id", "string", False), ("approval_id", "string"),
             ("pipeline_id", "string", False),
             ("execution_mode", "string", False), ("workspace_id", "string", False),
             ("started_at", "timestamp", False), ("completed_at", "timestamp"),
             ("status", "string", False), ("activation_revision", "string"),
             ("boundary_completed", "boolean", False),
             ("pipeline_version", "integer"),
             ("promotion_id", "string"), ("governed_notebook_id", "string"), ("execution_identity", "string"),
             ("run_schema_version", "integer"),
             ("operations", [("operation_key", "string", False),
                 ("table_id", "string"), ("source_type", "string"), ("source_id", "string"),
                 ("source_ids", "strings"), ("pipeline_role", "string", False),
                 ("contract_id", "string"), ("contract_version", "integer"), ("payload_sha256", "string"),
                 ("destination", {"struct": [(n,t,True if n in {"kind", "table_name"} else z) for n,t,z in BINDING_FIELDS if n != "table_id"] +
                     [("source_type", "string"), ("source_id", "string"), ("relative_path", "string"),
                      ("file_format", "string"), ("reader_options_json", "string")]}, False),
                 ("read_mode", "string"), ("write_mode", "string"), ("query_sha256", "string"),
                 ("read_parameters", {"struct": [("watermark_column", "string")]}),
                 ("write_parameters", {"struct": [(key, kind) for key, kind in CATALOGUE_NESTED_FIELDS["load_strategy_parameters_json"].items()]}),
                 ("repartition_by", "integer"),
                 ("source_table_ids", "strings", False), ("incremental_target_table_id", "string"),
                 ("rows_read", "long"), ("rows_written", "long"),
                 ("metrics", {"struct": [
                     ("rows_read", "long"), ("columns", "long"),
                     ("input_rows", "long"), ("input_columns", "long"),
                     ("rows_committed", "long"), ("rows_inserted", "long"),
                     ("rows_updated", "long"), ("rows_unchanged", "long"),
                     ("versions_inserted", "long"), ("versions_expired", "long"),
                     ("total_target_rows", "long"), ("measurement_source", "string"),
                 ]}),
                 ("status", "string", False), ("started_at", "timestamp"), ("completed_at", "timestamp"),
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
                ("table_id", "string"), ("source_id", "string"),
                ("table_name", "string"),
                ("contract_id", "string", False),
                ("contract_version", "integer", False),
                ("execution_type", "string", False),
                ("run_id", "string", False),
                ("workspace_id", "string", False),
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
                ("workspace_id", "string", False),
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
                ("snapshot_payload_json", "string"),
                *audit,
            ],
        ),
    }

    schemas = {name: schemas[name] for name in CANONICAL_METADATA_TABLES}
    if not logical:
        string_type = schemas["METADATA_DATA_CONTRACT"].fields[0].dataType
        for table, names in METADATA_JSON_COLUMNS.items():
            for field in schemas[table].fields:
                if field.name in names:
                    field.dataType = string_type
            schemas[table] = type(schemas[table])(schemas[table].fields)
    return schemas


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


def validate_metadata_value(value: Any, data_type: Any, *, field: str) -> Any:
    """Validate a typed logical metadata value without lossy scalar coercion.

    Missing nullable struct fields become null; unknown fields, null array
    elements, numeric overflow and scalar coercions fail closed.
    """
    import math

    if value is None:
        return None
    if hasattr(value, "asDict"):
        value = value.asDict(recursive=True)
    if hasattr(data_type, "fields"):
        if not isinstance(value, dict):
            raise ValueError(f"{field} must be an object.")
        unknown = set(value) - {item.name for item in data_type.fields}
        if unknown:
            raise ValueError(f"{field} contains unknown fields: {', '.join(sorted(unknown))}.")
        result = {}
        for item in data_type.fields:
            member = value.get(item.name)
            if member is None and not item.nullable:
                raise ValueError(f"{field}.{item.name} cannot be null.")
            result[item.name] = validate_metadata_value(member, item.dataType, field=f"{field}.{item.name}")
        return result
    if hasattr(data_type, "elementType"):
        if not isinstance(value, list) or any(item is None for item in value):
            raise ValueError(f"{field} must be an array of non-null elements.")
        return [validate_metadata_value(item, data_type.elementType, field=f"{field}[{index}]")
                for index, item in enumerate(value)]
    kind = type(data_type).__name__
    valid = False
    if kind == "StringType":
        valid = isinstance(value, str)
    elif kind == "BooleanType":
        valid = type(value) is bool
    elif kind in {"IntegerType", "LongType"}:
        bits = 32 if kind == "IntegerType" else 64
        valid = type(value) is int and -(2 ** (bits - 1)) <= value < 2 ** (bits - 1)
    elif kind == "TimestampType":
        try:
            parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else None
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO timestamp.") from exc
        if parsed is not None:
            return parsed if isinstance(value, datetime) else parsed.astimezone(UTC).replace(tzinfo=None) if parsed.tzinfo else parsed
    elif kind == "DoubleType":
        valid = type(value) in {int, float} and math.isfinite(value)
        if valid:
            return float(value)
    if not valid:
        raise ValueError(f"{field} must have type {metadata_schema_type_name(data_type)}.")
    return value


def coerce_metadata_row_types(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    """Return typed logical metadata; encode JSON fields at physical writes."""
    try:
        schema = metadata_table_schema_registry(logical=True).get(table_name)
    except Exception:
        schema = None
    if schema is None:
        return dict(row)
    coerced = dict(row)
    for field in getattr(schema, "fields", []):
        if field.name in coerced:
            if field.name in METADATA_JSON_COLUMNS.get(table_name, ()):
                # Runtime coercion requires native logical values; only the
                # physical row decoder accepts JSON text.
                coerced[field.name] = validate_metadata_value(coerced[field.name], field.dataType, field=field.name)
                if table_name == "METADATA_PIPELINE_RUN" and field.name == "operations":
                    coerced[field.name] = decode_metadata_row(table_name, {field.name: row[field.name]})[field.name]
            elif coerced[field.name] is None and field.nullable:
                coerced[field.name] = None
            else:
                if hasattr(field.dataType, "elementType") or hasattr(field.dataType, "fields"):
                    coerced[field.name] = _coerce_metadata_field(coerced[field.name], field.dataType)
                else:
                    coerced[field.name] = _coerce_metadata_value(coerced[field.name], type(field.dataType).__name__)
    return coerced


def metadata_json_schema(table_name: str) -> dict[str, Any]:
    """Return logical fields stored as JSON strings, with their Spark types."""
    schema = metadata_table_schema_registry(logical=True).get(table_name)
    names = METADATA_JSON_COLUMNS.get(table_name, ())
    return {field.name: field.dataType for field in schema.fields if field.name in names} if schema else {}


def parse_metadata_json(value: str, *, field: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and nonfinite constants."""
    import json

    def unique_object(pairs):
        result = {}
        for name, item in pairs:
            if name in result:
                raise ValueError(f"{field} contains duplicate JSON field {name}.")
            result[name] = item
        return result

    def invalid_constant(token):
        raise ValueError(f"{field} contains nonfinite JSON number {token}.")

    try:
        return json.loads(value, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{field} contains invalid JSON: {exc}") from exc


def decode_metadata_row(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    """Decode physical JSON metadata into validated logical dictionaries/lists.

    Native logical values are accepted for application calls, not as a physical
    schema fallback. Missing nullable struct members retain their explicit nulls.
    Additive profiling scope members stay absent in retained Run JSON so historical
    approved content hashes remain stable.
    """
    result = dict(row)
    required = table_name == "METADATA_PIPELINE_RUN"
    for name, kind in metadata_json_schema(table_name).items():
        if name not in result:
            continue
        value = result[name]
        if isinstance(value, str):
            value = parse_metadata_json(value, field=name)
        if value is None and required:
            raise ValueError(f"{table_name}.{name} cannot be null.")
        result[name] = validate_metadata_value(value, kind, field=name)
        if required and name == "operations":
            for original, decoded in zip(value, result[name]):
                for field in ("read_parameters", "write_parameters", "repartition_by", "source_type", "source_id", "source_ids"):
                    if field not in original:
                        decoded.pop(field, None)
                    elif isinstance(original[field], dict):
                        decoded[field] = {key: decoded[field][key] for key in original[field]}
                decoded["destination"] = {key: decoded["destination"][key] for key in original["destination"]}
        if required and name == "profiling":
            # Scope fields are additive JSON members. Do not inject them into
            # retained Run content and change a previously approved content hash.
            for original, decoded in zip(value, result[name]):
                for field in ("profile_scope", "profiling_max_rows"):
                    if field not in original:
                        decoded.pop(field, None)
    return result


def encode_metadata_row(table_name: str, row: dict[str, Any]) -> dict[str, Any]:
    """Encode logical JSON fields for physical writes without changing other data.

    Existing valid JSON text is retained exactly, allowing whole-row Run CAS to
    compare the actual committed bytes, including historical whitespace/key order.
    """
    import json

    result = dict(row)
    decoded = decode_metadata_row(table_name, row)
    for name in metadata_json_schema(table_name):
        if name in result and not isinstance(result[name], str):
            value = decoded[name]
            result[name] = None if value is None else json.dumps(
                value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                allow_nan=False, default=_metadata_json_default,
            )
    return result


def _metadata_json_default(value):
    """Encode native timestamp instants consistently with retained Run hashes."""
    if isinstance(value, datetime):
        return (value.astimezone(UTC).replace(tzinfo=None) if value.tzinfo else value).isoformat()
    raise TypeError(f"Unsupported JSON metadata value: {type(value).__name__}.")


def decode_metadata_dataframe(table_name: str, frame: Any) -> Any:
    """Decode JSON in Spark for authoritative profiling-history aggregation.

    Strict validation uses the same row codec before typed parsing; malformed
    JSON must never silently turn into null or an empty completion history.
    """
    from pyspark.sql import functions as F
    from pyspark.sql.types import StringType

    for name, kind in metadata_json_schema(table_name).items():
        if name not in frame.columns:
            continue

        def validate(value, name=name):
            decode_metadata_row(table_name, {name: value})
            return value

        checked = F.udf(validate, StringType())(F.col(name))
        frame = frame.withColumn(name, F.from_json(checked, kind, {"mode": "FAILFAST", "timeZone": "UTC"}))
    return frame


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
