"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from fabricops_kit.io.shared import get_spark_session

from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

from typing import Any

from .metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    CATALOGUE_NESTED_FIELDS,
    validate_metadata_value,
    metadata_json_schema,
    decode_metadata_row,
    encode_metadata_row,
    parse_metadata_json,
    RETIRED_PREVIEW_METADATA_TABLES,
    GOVERNANCE_METADATA_TABLES,
    ENGINEERING_METADATA_TABLES,
    metadata_table_physical_schema,
    metadata_schema_type_name,
    metadata_table_field_names,
    metadata_table_schema_registry,
)
from .shared import FrameworkConfig, get_store, is_table_not_found_error, validate_framework_config


def _schema_fields_by_name(schema: Any) -> dict[str, Any]:
    """Return schema fields keyed by name for Spark-like schemas."""
    return {field.name: field for field in getattr(schema, "fields", [])}


def _table_column_names(table: Any) -> list[str]:
    """Return physical table column names without depending on nullability."""
    if table is None:
        return []
    schema = getattr(table, "schema", None)
    if schema is not None:
        names = list(getattr(schema, "fieldNames", lambda: [])())
        if names:
            return names
    return list(getattr(table, "columns", []) or [])


def _retired_table_is_missing(exc):
    """Recognize table/path absence without swallowing generic storage failures."""
    if isinstance(exc, (PermissionError, OSError)):
        return False
    message = str(exc).lower()
    return any(token in message for token in (
        "[table_or_view_not_found]", "[path_not_found]", "[delta_table_not_found]",
        "table or view not found", "table not found", "table does not exist",
        "delta table doesn't exist",
    ))


def _retired_preview_warnings(*, config, spark, context):
    """Probe declared retired names without evaluating their historical rows."""
    warnings = []
    schemas = dict.fromkeys((config.governance_metadata_schema, config.engineering_metadata_schema))
    for schema in schemas:
        for table_name, retirement in RETIRED_PREVIEW_METADATA_TABLES.items():
            physical_name = f"{schema}.{table_name}"
            try:
                # Delta loading resolves presence/schema only; never run a row action.
                read_lakehouse_table(table_name, store="Metadata", schema=schema,
                                     context={**(context or {}), "_spark_session": spark})
            except Exception as exc:
                if not _retired_table_is_missing(exc):
                    warnings.append(
                        f"Unable to inspect {physical_name} in the configured Metadata Lakehouse: "
                        f"{type(exc).__name__}: {exc}. Retirement presence is unknown; "
                        "check access/storage and rerun setup. This diagnostic is advisory."
                    )
            else:
                warnings.append(
                    f"{physical_name} in the configured Metadata Lakehouse is a former Preview table "
                    f"that is no longer supported (retired in v{retirement['retired_in']}). "
                    f"{retirement['guidance']} Required definitions, progress and history remain untouched; "
                    "these tables do not participate in current runtime authority. "
                    "Setup never deletes their contents or treats them as canonical metadata."
                )
    return warnings


def _validate_existing_metadata_schema(
    table_name: str,
    existing_schema: Any,
    expected_schema: Any,
    *,
    allow_missing: bool = False,
) -> list[str]:
    """Validate canonical field types and return missing canonical columns."""
    existing = _schema_fields_by_name(existing_schema)
    expected = _schema_fields_by_name(expected_schema)
    if not existing:
        existing = {name: None for name in getattr(existing_schema, "fieldNames", lambda: [])()}
    if table_name == "METADATA_DATA_PROFILED" and "frequency_json" in existing:
        raise ValueError("METADATA_DATA_PROFILED has unexpected legacy column: frequency_json.")
    provenance = {"pipeline_version", "promotion_id", "governed_notebook_id", "execution_identity", "run_schema_version"}
    supported_run_addition = (table_name == "METADATA_PIPELINE_RUN" and allow_missing
        and not (set(existing) - set(expected)) and set(expected) - set(existing) <= provenance)
    if table_name in {"METADATA_PIPELINE_RUN", "METADATA_PIPELINE_REGISTRY", "METADATA_DATA_CONTRACT_ACTIVATION"} and set(expected) != set(existing) and not supported_run_addition:
        raise ValueError(
            f"Incompatible {table_name} physical schema. Required identity and execution fields must match the canonical schema. "
            "Existing data has been preserved; automatic schema evolution is unsafe for this layout."
        )
    if table_name == "METADATA_PROCESSING_STATE" and (
        "observation_status" in existing or "publication_payload_json" in existing
        or set(expected) - set(existing)
    ):
        raise ValueError(
            "Incompatible METADATA_PROCESSING_STATE schema. Existing checkpoints and publication receipts have been preserved. "
            "Required processing identity and progress fields cannot be inferred safely."
        )
    missing = [name for name in expected if name not in existing]
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
        raise ValueError(
            f"{table_name} physical schema does not match the canonical FabricOps metadata schema: "
            + "; ".join(mismatches)
            + "."
        )
    if missing and not allow_missing:
        raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
    return missing


def _add_missing_metadata_columns(
    *,
    spark: Any,
    table_name: str,
    metadata_schema: str,
    expected_schema: Any,
    missing_columns: list[str],
    context: dict[str, Any],
) -> None:
    """Add missing canonical columns through an empty Delta merge-schema append."""
    expected = _schema_fields_by_name(expected_schema)
    additive_schema = expected_schema.__class__([expected[name] for name in missing_columns])
    empty_frame = spark.createDataFrame([], schema=additive_schema)
    write_lakehouse_table(
        empty_frame,
        table_name,
        store="Metadata",
        schema=metadata_schema,
        mode="append",
        options={"mergeSchema": "true"},
        verbose=False,
        context=context,
    )


def _parse_catalogue_value(value, data_type, *, field, historical):
    """Parse historical JSON strictly; native runtime values never use this path."""
    if historical and value is not None:
        value = None if not value.strip() else parse_metadata_json(value, field=field)
        if field == "profile_key_candidates_json" and isinstance(value, list):
            value = {"status": None, "max_combination_width": None, "candidates": value}
    return validate_metadata_value(value, data_type, field=field)


def _upgrade_json_metadata(*, spark, table, table_name, expected_schema, metadata_schema, context):
    """Upgrade known Run/Catalogue nested fields in one pinned Delta transaction.

    Schema and replacement files commit together. Whole-table read tracking and
    metadata conflict checks prevent loss of concurrent updates/blind appends.
    Already valid JSON columns retain their exact bytes and require no rewrite.
    """
    import json
    from uuid import uuid4

    from fabricops_kit.io.shared import resolve_configured_lakehouse_table

    if not hasattr(table, "schema"):
        return table, None
    logical_fields = metadata_json_schema(table_name)
    expected = _schema_fields_by_name(expected_schema)

    def inspect(frame):
        actual = _schema_fields_by_name(frame.schema)
        converted = set()
        for name, kind in logical_fields.items():
            if name not in actual:
                continue
            physical = metadata_schema_type_name(actual[name].dataType)
            if physical == metadata_schema_type_name(kind):
                converted.add(name)
            elif physical != "string":
                raise ValueError(f"Unsupported {table_name} physical type for {name}: {physical}.")
        compatible = frame.schema.__class__([expected[f.name] if f.name in converted else f for f in frame.schema.fields])
        _validate_existing_metadata_schema(table_name, compatible, expected_schema, allow_missing=True)
        return converted

    def convert(row):
        values = row.asDict(recursive=True)
        for name, kind in logical_fields.items():
            value = values.get(name)
            if table_name == "METADATA_DATA_CATALOGUE" and isinstance(value, str):
                parsed = _parse_catalogue_value(value, kind, field=name, historical=True)
                # Only historical blanks/list-only candidates require a JSON
                # rewrite; supported object strings retain their original bytes.
                if parsed is None or not value.strip() or isinstance(parse_metadata_json(value, field=name), list):
                    values[name] = parsed
        decoded = decode_metadata_row(table_name, values)
        if table_name == "METADATA_PIPELINE_RUN":
            from fabricops_kit.pipeline.shared import validate_pipeline_run
            validate_pipeline_run(decoded)
            for field in expected_schema.fields:
                if not field.nullable and decoded.get(field.name) is None:
                    raise ValueError(f"{table_name}.{field.name} cannot be null.")
        return encode_metadata_row(table_name, values)

    def validate(frame):
        changed = set()
        has_rows = False
        for row in frame.toLocalIterator():
            has_rows = True
            values = row.asDict(recursive=True)
            converted = convert(row)
            changed.update(name for name in logical_fields if converted.get(name) != values.get(name))
        if has_rows and table_name == "METADATA_PIPELINE_RUN" and frame.groupBy("run_id").count().where("count > 1").limit(1).count():
            raise ValueError("Duplicate Pipeline Run identities; existing history is preserved and schema evolution is blocked.")
        return changed

    converted = inspect(table)
    # All-JSON schemas are validated on every setup, but never rewritten merely
    # to canonicalize whitespace/object-key order in retained evidence.
    if not converted and not validate(table):
        return table, None

    from pyspark.sql import functions as F
    from pyspark.sql.types import StructField, StructType

    _, _, _, path = resolve_configured_lakehouse_table(
        "Metadata", table_name, metadata_schema, context=context)
    jvm = spark._jvm
    delta = jvm.org.apache.spark.sql.delta
    log = delta.DeltaLog.forTable(spark._jsparkSession, path)
    txn = log.startTransaction()
    version = int(txn.readVersion())
    txn.readWholeTable()
    files = txn.filterFiles()
    source = spark.read.format("delta").option("versionAsOf", version).load(path)
    converted = inspect(source)
    converted.update(validate(source))
    if not converted:
        return source, None
    actual = _schema_fields_by_name(source.schema)
    target_schema = StructType([
        StructField(f.name, expected[f.name].dataType, f.nullable, f.metadata)
        if f.name in logical_fields else f for f in source.schema.fields
    ] + [StructField(f.name, f.dataType, True, f.metadata) for f in expected_schema.fields if f.name not in actual])
    stage = path.rstrip("/") + "_json_upgrade_staging/" + str(uuid4())
    fs_path = jvm.org.apache.hadoop.fs.Path(stage)
    fs = fs_path.getFileSystem(spark._jsc.hadoopConfiguration())
    try:
        replacement = spark.createDataFrame(source.rdd.map(convert), target_schema)
        replacement.write.mode("errorifexists").parquet(stage)
        replacement = spark.read.schema(target_schema).parquet(stage)
        metadata = json.loads(txn.metadata().json())
        physical_schema = StructType.fromJson(json.loads(metadata["metaData"]["schemaString"]))
        replacement_metadata_schema = StructType([
            StructField(f.name, expected[f.name].dataType, f.nullable, f.metadata)
            if f.name in logical_fields else f for f in physical_schema.fields
        ] + [f for f in target_schema.fields if f.name not in actual])
        metadata["metaData"]["schemaString"] = replacement_metadata_schema.json()
        txn.updateMetadata(delta.actions.Action.fromJson(json.dumps(metadata)), False)
        added = txn.writeFiles(replacement._jdf)
        actions = jvm.java.util.ArrayList()
        for index in range(files.size()):
            actions.add(files.apply(index).remove())
        for index in range(added.size()):
            actions.add(added.apply(index))
        seq = jvm.scala.collection.JavaConverters.asScalaBufferConverter(actions).asScala().toSeq()
        recovery = json.dumps({"fabricops_json_upgrade": 1, "table": table_name, "pre_upgrade_version": version})
        option = jvm.scala.Option
        from py4j.protocol import Py4JError

        write_args = (jvm.org.apache.spark.sql.SaveMode.Overwrite,
                      option.empty(), option.empty(), option.apply(recovery))
        try:
            operation = delta.DeltaOperations.Write(
                *write_args, option.empty(), option.empty(), option.empty())
        except Py4JError as exc:
            if ("Constructor org.apache.spark.sql.delta.DeltaOperations$Write" not in str(exc)
                    or "does not exist" not in str(exc)):
                raise
            operation = delta.DeltaOperations.Write(*write_args)
        committed_version = int(txn.commit(seq, operation))
        committed = spark.read.format("delta").option("versionAsOf", committed_version).load(path)
        if committed.schema != replacement.schema:
            raise RuntimeError(f"{table_name} upgrade committed but schema verification failed; inspect Delta history.")

        def serialized(frame):
            return frame.select(F.to_json(F.struct(*[F.col('`' + name.replace('`', '``') + '`')
                for name in frame.columns]), options={"ignoreNullFields": "false", "timeZone": "UTC",
                    "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                    "timestampNTZFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"}).alias("row"))

        before, after = serialized(replacement), serialized(committed)
        if before.exceptAll(after).limit(1).count() or after.exceptAll(before).limit(1).count():
            raise RuntimeError(f"{table_name} upgrade committed but data verification failed; inspect Delta history.")
        return spark.read.format("delta").load(path), {
            "pre_upgrade_version": version, "upgrade_version": committed_version,
            "converted_columns": sorted(converted),
        }
    finally:
        fs.delete(fs_path, True)


def _result(table_name: str, status: str, message: str, *, error_type: str | None = None) -> dict[str, Any]:
    """Return one per-table setup result."""
    item = {"table": table_name, "status": status, "message": message}
    if error_type:
        item["error_type"] = error_type
    return item


def _active_steward_presence(steward_rows: Any) -> int:
    """Return 1 when any active steward row exists, otherwise 0."""
    try:
        if steward_rows is None:
            return 0
        if hasattr(steward_rows, "where"):
            steward_rows = steward_rows.where("is_active = true")
        if hasattr(steward_rows, "limit"):
            steward_rows = steward_rows.limit(1)
        if hasattr(steward_rows, "take"):
            return 1 if steward_rows.take(1) else 0
        if hasattr(steward_rows, "head"):
            return 1 if steward_rows.head(1) else 0
        if hasattr(steward_rows, "first"):
            return 1 if steward_rows.first() is not None else 0
        if hasattr(steward_rows, "collect"):
            return 1 if steward_rows.collect()[:1] else 0
    except Exception:
        return 0
    return 0


def _print_setup_summary(
    *,
    total: int,
    created: list[str],
    evolved: list[str],
    validated: list[str],
    failed: list[str],
    table_results: dict[str, dict[str, Any]],
    active_stewards: int,
) -> None:
    """Print concise notebook-facing setup output after per-table progress."""
    active_label = "Yes" if active_stewards else "No"
    if failed:
        successful_count = len(created) + len(evolved) + len(validated)
        print("\nFabricOps metadata setup completed with failures.")
        print(f"Successful: {successful_count:,}/{total:,}")
        print(f"Failed: {len(failed):,}/{total:,}\n")
        print("Failed tables:")
        for table_name in failed:
            print(f"- {table_name}: {table_results[table_name].get('message', '')}")
        print(f"Active steward present: {active_label}")
        return
    if created or evolved:
        print(f"\nFabricOps metadata setup complete ({total:,}/{total:,}).")
        print(f"Created: {len(created):,}")
        print(f"Evolved: {len(evolved):,}")
        print(f"Validated: {len(validated):,}")
        if created:
            print("Created tables:")
            for table_name in created:
                print(f"- {table_name}")
        if evolved:
            print("Evolved tables:")
            for table_name in evolved:
                print(f"- {table_name}")
        print(f"Active steward present: {active_label}")
        return
    print(f"\nFabricOps metadata tables ready ({total:,}/{total:,}).")
    print(f"Active steward present: {active_label}")


def setup_metadata_tables(
    *,
    config: FrameworkConfig | dict[str, Any],
    workspace_id: str,
    require_active_steward: bool = False,
    verbose: bool = True,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Create, validate and safely evolve the 14 canonical metadata tables.

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any]
        Configuration containing the selected workspace's central Metadata
        Lakehouse. Metadata must be a schema-enabled Lakehouse.
    workspace_id : str
        Configuration scope used to resolve the Metadata store.
    require_active_steward : bool, default=False
        Require an active Data Steward after table setup. No steward is created.
    verbose : bool, default=True
        Print concise per-table creation, evolution and readiness results.
    raise_on_failure : bool, default=False
        Raise after all tables have been processed when any table fails.

    Returns
    -------
    dict[str, Any]
        Overall readiness, configured ownership schemas, canonical table names,
        created/evolved/validated/failed tables, per-table results, steward
        readiness and advisory diagnostics for noncanonical metadata tables.

    Raises
    ------
    ValueError
        If configuration is invalid, Metadata is not a schema-enabled Lakehouse,
        or an explicitly required active steward is absent.
    RuntimeError
        If Spark is unavailable or raise_on_failure is enabled and a table fails.

    Notes
    -----
    Missing tables are created empty with error-if-exists semantics. Registry
    and Contract Activation use Serializable isolation; Processing State is
    created or upgraded to Serializable for atomic Source Drift acceptance.
    Setup never manufactures
    approvals, populates business metadata, deletes rows or replaces business
    targets. Governance definitions and activation are independent workflows.

    Compatible missing columns are added automatically. Catalogue and Pipeline
    Run collection fields are stored as validated JSON strings; supported native
    collections are converted atomically with tracked Delta reads and exact
    schema/data readback. Existing rows, audit values, extension fields, table
    identity/properties and Delta transaction identities are preserved. Run
    provenance additions are nullable and preserve retained content hashes.
    Repeated setup validates compliant tables without rewriting them.

    Processing State observations, checkpoints, accepted baselines and publication
    receipts remain intact. Missing progress is never inferred for populated
    targets. Incompatible identity layouts, incorrect types, malformed JSON and
    duplicate Run identities fail explicitly with the existing data preserved.
    A failure in one table does not prevent validation of the remaining tables.
    Physical nullability and field order are not rewritten.

    Governed admission remains blocked pending signed-in Fabric acceptance.
    Retirement presence diagnostics are advisory; unsupported tables are never
    read as canonical authority or automatically deleted.

    Examples
    --------
    >>> result = setup_metadata_tables(config=CONFIG, workspace_id=WORKSPACE_ID)
    >>> result["status"]
    'ready'

    """
    active_workspace_id = workspace_id
    spark = get_spark_session()
    normalized = validate_framework_config(config)
    metadata_store = get_store(config=normalized, active_workspace_id=active_workspace_id, store="Metadata")
    if getattr(metadata_store, "kind", None) != "lakehouse":
        raise ValueError(f"Target '{active_workspace_id}/metadata' is not a lakehouse store.")
    if metadata_store.schema_enabled is not True:
        raise ValueError("FabricOps Metadata Lakehouse must be schema-enabled.")
    context = {"config": normalized, "scope_workspace_id": active_workspace_id, "_fabricops_suppress_io_log": not verbose}
    registry = metadata_table_schema_registry()

    warnings = _retired_preview_warnings(config=normalized, spark=spark, context=context)

    table_results: dict[str, dict[str, Any]] = {}
    created_tables: list[str] = []
    evolved_tables: list[str] = []
    validated_tables: list[str] = []
    failed_tables: list[str] = []

    total_tables = len(registry)
    steward_table = None

    for index, (table_name, schema) in enumerate(registry.items(), start=1):
        resolved_metadata_schema = metadata_table_physical_schema(normalized, table_name)
        try:
            created = False
            try:
                table = read_lakehouse_table(
                    table_name, store="Metadata", schema=resolved_metadata_schema, context={**(context or {}), "_spark_session": spark}
                )
            except Exception as exc:
                if not is_table_not_found_error(exc):
                    raise RuntimeError(
                        f"Unable to read metadata table {table_name!r}. Original {type(exc).__name__}: {exc}"
                    ) from exc
                initial_rows = []
                empty_frame = spark.createDataFrame(initial_rows, schema=schema)
                write_lakehouse_table(
                    empty_frame,
                    table_name,
                    store="Metadata",
                    schema=resolved_metadata_schema,
                    mode="errorifexists",
                    verbose=False,
                    context=context,
                    options={"delta.isolationLevel": "Serializable"} if table_name in {"METADATA_PIPELINE_REGISTRY", "METADATA_DATA_CONTRACT_ACTIVATION", "METADATA_PIPELINE_ACTIVATION", "METADATA_PROCESSING_STATE"} else None,
                )
                created = True
                table = read_lakehouse_table(
                    table_name, store="Metadata", schema=resolved_metadata_schema, context={**(context or {}), "_spark_session": spark}
                )
            if table_name == "METADATA_PROCESSING_STATE" and not created and hasattr(table, "sparkSession"):
                from delta.tables import DeltaTable
                from fabricops_kit.io.shared import resolve_configured_lakehouse_table
                from fabricops_kit.io.shared import retry_delta_metadata
                _, _, _, state_path = resolve_configured_lakehouse_table("Metadata", table_name,
                    resolved_metadata_schema, context=context)
                properties = DeltaTable.forPath(spark, state_path).detail().select("properties").first()["properties"]
                if properties.get("delta.isolationLevel") != "Serializable":
                    retry_delta_metadata(lambda: spark.sql(f"ALTER TABLE delta.`{state_path.replace('`', '``')}` SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')"))
            upgrade = None
            if not created and hasattr(table, "schema") and table_name in {"METADATA_PIPELINE_REGISTRY", "METADATA_DATA_CONTRACT_ACTIVATION", "METADATA_PIPELINE_ACTIVATION"}:
                _validate_existing_metadata_schema(table_name, table.schema, schema)
            if metadata_json_schema(table_name):
                table, upgrade = _upgrade_json_metadata(
                    spark=spark, table=table, table_name=table_name, expected_schema=schema,
                    metadata_schema=resolved_metadata_schema, context=context)
            evolved_columns: list[str] = []
            if not created:
                columns = _table_column_names(table)
                if table_name == "METADATA_DATA_PROFILED" and "frequency_json" in columns:
                    raise ValueError("METADATA_DATA_PROFILED has unexpected legacy column: frequency_json.")
                if table is not None and hasattr(table, "schema"):
                    evolved_columns = _validate_existing_metadata_schema(
                        table_name, table.schema, schema, allow_missing=True
                    )
                else:
                    expected_columns = metadata_table_field_names(schema)
                    evolved_columns = [field for field in expected_columns if field not in columns]
                if evolved_columns:
                    _add_missing_metadata_columns(
                        spark=spark,
                        table_name=table_name,
                        metadata_schema=resolved_metadata_schema,
                        expected_schema=schema,
                        missing_columns=evolved_columns,
                        context=context,
                    )
                    table = read_lakehouse_table(
                        table_name,
                        store="Metadata",
                        schema=resolved_metadata_schema,
                        context={**(context or {}), "_spark_session": spark},
                    )
            if table is not None and hasattr(table, "schema"):
                _validate_existing_metadata_schema(table_name, table.schema, schema)
            else:
                columns = _table_column_names(table)
                missing = [field for field in metadata_table_field_names(schema) if field not in columns]
                if missing:
                    raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}.")
            if table_name == "METADATA_DATA_STEWARD":
                steward_table = table
            if created:
                created_tables.append(table_name)
                table_results[table_name] = _result(table_name, "created", "Metadata table was created and validated.")
                if verbose:
                    print(f"[{index:,}/{total_tables:,}] Created {table_name}\n")
            elif upgrade:
                evolved_tables.append(table_name)
                table_results[table_name] = {
                    **_result(table_name, "evolved", "JSON metadata automatically upgraded to SQL-compatible strings and verified."),
                    **upgrade,
                }
                if verbose:
                    print(f"[{index:,}/{total_tables:,}] Automatically upgraded {table_name} to SQL-compatible JSON strings\n")
            elif evolved_columns:
                evolved_tables.append(table_name)
                table_results[table_name] = {
                    **_result(
                        table_name,
                        "evolved",
                        "Existing metadata table was additively evolved and validated.",
                    ),
                    "added_columns": evolved_columns,
                }
                if verbose:
                    print(f"[{index:,}/{total_tables:,}] Evolved {table_name}")
                    print(f"       Added columns: {', '.join(evolved_columns)}\n")
            else:
                validated_tables.append(table_name)
                table_results[table_name] = _result(
                    table_name, "validated", "Existing metadata table schema is compatible."
                )
        except Exception as exc:  # continue after per-table failures
            failed_tables.append(table_name)
            table_results[table_name] = _result(table_name, "failed", f"{exc}", error_type=type(exc).__name__)
            if verbose:
                print(f"[{index:,}/{total_tables:,}] Failed {table_name}")
                print(f"       {exc}\n")

    active_stewards = _active_steward_presence(steward_table)

    successful = created_tables + evolved_tables + validated_tables
    status = "ready" if not failed_tables else ("partial_failure" if successful else "failed")
    data_agreement_tables = [
        "METADATA_DATA_STEWARD", "METADATA_DATA_AGREEMENT", "METADATA_DATA_CONTRACT",
    ]
    data_agreement_failed = [table for table in data_agreement_tables if table in failed_tables]
    data_agreement = {
        "status": "failed" if data_agreement_failed else ("ready" if active_stewards else "not_ready"),
        "tables": data_agreement_tables,
        "created_tables": [table for table in data_agreement_tables if table in created_tables],
        "evolved_tables": [table for table in data_agreement_tables if table in evolved_tables],
        "validated_tables": [table for table in data_agreement_tables if table in validated_tables],
        "failed_tables": data_agreement_failed,
        "active_steward_count": active_stewards,
    }
    if require_active_steward and not active_stewards:
        raise ValueError("METADATA_DATA_STEWARD has no active steward rows yet.")
    governance_tables = list(GOVERNANCE_METADATA_TABLES)
    governance_failed = [table for table in governance_tables if table in failed_tables]
    governance = {
        "status": "failed" if governance_failed else "ready",
        "tables": governance_tables,
        "created_tables": [table for table in governance_tables if table in created_tables],
        "evolved_tables": [table for table in governance_tables if table in evolved_tables],
        "validated_tables": [table for table in governance_tables if table in validated_tables],
        "failed_tables": governance_failed,
    }
    engineering_tables = list(ENGINEERING_METADATA_TABLES)
    engineering_failed = [table for table in engineering_tables if table in failed_tables]
    engineering = {
        "status": "failed" if engineering_failed else "ready",
        "tables": engineering_tables,
        "created_tables": [table for table in engineering_tables if table in created_tables],
        "evolved_tables": [table for table in engineering_tables if table in evolved_tables],
        "validated_tables": [table for table in engineering_tables if table in validated_tables],
        "failed_tables": engineering_failed,
    }
    metadata_schemas = {
        "governance": normalized.governance_metadata_schema,
        "engineering": normalized.engineering_metadata_schema,
    }
    fully_qualified_tables = [f"{metadata_table_physical_schema(normalized, table)}.{table}" for table in registry]
    result = {
        "status": status,
        "governed_execution": {"status": "blocked", "reason": "Trusted deployment verification is pending; activation candidates grant no publication authority."},
        "data_agreement": data_agreement,
        "governance": governance,
        "tables": list(registry),
        "table_results": table_results,
        "metadata_schemas": metadata_schemas,
        "engineering": engineering,
        "fully_qualified_tables": fully_qualified_tables,
        "created_tables": created_tables,
        "evolved_tables": evolved_tables,
        "validated_tables": validated_tables,
        "failed_tables": failed_tables,
        "created_or_checked_tables": successful,
        "warnings": warnings,
        "active_metadata_tables": successful,
        "active_metadata_table_count": len(successful),
    }
    if verbose:
        for warning in warnings:
            print(f"Warning: {warning}")
        _print_setup_summary(
            total=total_tables,
            created=created_tables,
            evolved=evolved_tables,
            validated=validated_tables,
            failed=failed_tables,
            table_results=table_results,
            active_stewards=active_stewards,
        )
    if raise_on_failure and failed_tables:
        detail = "; ".join(f"{table}: {table_results[table]['message']}" for table in failed_tables)
        raise RuntimeError(f"FabricOps metadata setup failed for {len(failed_tables)} table(s): {detail}")
    return result


__all__ = ["setup_metadata_tables"]
