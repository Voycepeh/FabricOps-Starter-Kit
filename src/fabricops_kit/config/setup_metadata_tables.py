"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

from typing import Any

from .metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    CATALOGUE_NESTED_FIELDS,
    validate_catalogue_value,
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
                                     spark_session=spark, context=context)
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
                    f"{retirement['guidance']} Preserve required definitions, progress or history, "
                    "then delete this table or explicitly map/migrate retained records. "
                    "Do not blindly append old rows into current tables. Setup does not migrate or delete data."
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
    if table_name in {"METADATA_PIPELINE_RUN", "METADATA_PIPELINE_REGISTRY"} and set(expected) != set(existing):
        raise ValueError(
            f"Unsupported {table_name} physical schema. Stop writers, back up and reconcile retained history; "
            "follow docs/maintainer/metadata-v2-target-model.md#joint-redesign-rollout-and-reset-policy. "
            "Automatic additive evolution is unsafe."
        )
    if table_name == "METADATA_PROCESSING_STATE" and (
        "observation_status" in existing or "publication_payload_json" in existing
        or set(expected) - set(existing)
    ):
        raise ValueError(
            "Unsupported legacy METADATA_PROCESSING_STATE schema. Stop writers, archive and reconcile "
            "publication progress, then explicitly migrate or reset this Preview table; "
            "see docs/maintainer/metadata-v2-target-model.md#processing-state-upgrade. "
            "Automatic additive evolution is unsafe."
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
    import json

    def unique_object(pairs):
        result = {}
        for name, item in pairs:
            if name in result:
                raise ValueError(f"{field} contains duplicate JSON field {name}.")
            result[name] = item
        return result

    if historical and value is not None:
        if not value.strip():
            value = None  # Historical empty/whitespace strings mean uncaptured.
        else:
            try:
                value = json.loads(value, object_pairs_hook=unique_object,
                                   parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{field} contains invalid JSON: {exc}") from exc
        if field == "profile_key_candidates_json" and isinstance(value, list):
            value = {"status": None, "max_combination_width": None, "candidates": value}
    return validate_catalogue_value(value, data_type, field=field)


def _upgrade_catalogue(*, spark, table, expected_schema, metadata_schema, context):
    """Validate and atomically replace only the supported Catalogue string types.

    Delta's optimistic transaction pins the source snapshot, tracks a whole-table
    read and changes metadata in the same commit as all file removals/additions.
    Metadata-changing transactions conflict with blind appends as well as normal
    writers under Delta's default WriteSerializable isolation. No external lock
    or check-then-overwrite window is used.
    """
    import json
    from uuid import uuid4

    from fabricops_kit.io.shared import resolve_configured_lakehouse_table

    # Keep lightweight setup fakes usable; real Spark tables always have schema.
    if not hasattr(table, "schema"):
        return table, None
    expected = _schema_fields_by_name(expected_schema)
    actual = _schema_fields_by_name(table.schema)
    historical = set()
    for name in CATALOGUE_NESTED_FIELDS:
        if name not in actual:
            continue
        kind = metadata_schema_type_name(actual[name].dataType)
        if kind == "string":
            historical.add(name)
        elif kind != metadata_schema_type_name(expected[name].dataType):
            raise ValueError(f"Unsupported Catalogue physical type for {name}: {kind}.")
    # Validate all other physical fields before starting any mutation, including
    # additive evolution. Extra physical columns are retained in their order.
    compatible = table.schema.__class__([expected[f.name] if f.name in historical else f for f in table.schema.fields])
    _validate_existing_metadata_schema("METADATA_DATA_CATALOGUE", compatible, expected_schema, allow_missing=True)
    if not historical:
        for row in table.select(*[name for name in CATALOGUE_NESTED_FIELDS if name in actual]).toLocalIterator():
            for name, value in row.asDict(recursive=True).items():
                _parse_catalogue_value(value, expected[name].dataType, field=name, historical=False)
        return table, None

    from pyspark.sql import functions as F
    from pyspark.sql.types import StructField, StructType

    _, _, _, path = resolve_configured_lakehouse_table(
        "Metadata", "METADATA_DATA_CATALOGUE", metadata_schema, context=context)
    jvm = spark._jvm
    delta = jvm.org.apache.spark.sql.delta
    log = delta.DeltaLog.forTable(spark._jsparkSession, path)
    txn = log.startTransaction()
    version = int(txn.readVersion())
    txn.readWholeTable()
    files = txn.filterFiles()
    source = spark.read.format("delta").option("versionAsOf", version).load(path)
    # Resolve again from the pinned snapshot: concurrent setup may already have
    # committed between the initial schema probe and transaction acquisition.
    actual = _schema_fields_by_name(source.schema)
    historical = {name for name in CATALOGUE_NESTED_FIELDS if name in actual
                  and metadata_schema_type_name(actual[name].dataType) == "string"}
    compatible = StructType([expected[f.name] if f.name in historical else f for f in source.schema.fields])
    _validate_existing_metadata_schema("METADATA_DATA_CATALOGUE", compatible, expected_schema, allow_missing=True)
    if not historical:
        return _upgrade_catalogue(spark=spark, table=source, expected_schema=expected_schema,
                                  metadata_schema=metadata_schema, context=context)
    target_schema = StructType([
        StructField(f.name, expected[f.name].dataType, f.nullable, f.metadata)
        if f.name in historical else f for f in source.schema.fields
    ] + [StructField(f.name, f.dataType, True, f.metadata) for f in expected_schema.fields if f.name not in actual])

    def convert(row):
        values = row.asDict(recursive=True)
        for name in CATALOGUE_NESTED_FIELDS:
            values[name] = _parse_catalogue_value(values.get(name), expected[name].dataType,
                                                field=name, historical=name in historical)
        return values

    # The separate durable staging path severs the read lineage before any
    # Catalogue mutation. A process interruption leaves only disposable staging
    # files; Delta's log remains the sole authority on whether conversion ran.
    stage = path.rstrip("/") + "_catalogue_upgrade_staging/" + str(uuid4())
    fs_path = jvm.org.apache.hadoop.fs.Path(stage)
    fs = fs_path.getFileSystem(spark._jsc.hadoopConfiguration())
    try:
        replacement = spark.createDataFrame(source.rdd.map(convert), target_schema)
        replacement.write.mode("errorifexists").parquet(stage)
        replacement = spark.read.schema(target_schema).parquet(stage)
        metadata = json.loads(txn.metadata().json())
        # Spark's read schema hides Delta column-mapping IDs/physical names.
        # Retain those from the transaction metadata, including unchanged nested
        # extension columns. Delta assigns IDs only to the new struct members.
        physical_schema = StructType.fromJson(json.loads(metadata["metaData"]["schemaString"]))
        replacement_metadata_schema = StructType([
            StructField(f.name, expected[f.name].dataType, f.nullable, f.metadata)
            if f.name in historical else f for f in physical_schema.fields
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
        recovery = json.dumps({"fabricops_catalogue_upgrade": 1, "pre_upgrade_version": version})
        option = jvm.scala.Option
        # Delta 4.2 adds three optional Write parameters; the persisted-Delta
        # regression runtime (3.3) still exposes the four-argument constructor.
        # Bind to the extended signature first without changing the transaction.
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
            raise RuntimeError("Catalogue upgrade committed but schema verification failed; inspect Delta history.")
        def serialized(frame):
            return frame.select(F.to_json(F.struct(*[F.col('`' + name.replace('`', '``') + '`')
                for name in frame.columns]), options={"ignoreNullFields": "false", "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                                                    "timestampNTZFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"}).alias("row"))
        before, after = serialized(replacement), serialized(committed)
        if before.exceptAll(after).limit(1).count() or after.exceptAll(before).limit(1).count():
            raise RuntimeError("Catalogue upgrade committed but data verification failed; inspect Delta history.")
        return spark.read.format("delta").load(path), {
            "pre_upgrade_version": version, "upgrade_version": committed_version,
            "converted_columns": sorted(historical),
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
        print(f"Successful: {successful_count}/{total}")
        print(f"Failed: {len(failed)}/{total}\n")
        print("Failed tables:")
        for table_name in failed:
            print(f"- {table_name}: {table_results[table_name].get('message', '')}")
        print(f"Active steward present: {active_label}")
        return
    if created or evolved:
        print(f"\nFabricOps metadata setup complete ({total}/{total}).")
        print(f"Created: {len(created)}")
        print(f"Evolved: {len(evolved)}")
        print(f"Validated: {len(validated)}")
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
    print(f"\nFabricOps metadata tables ready ({total}/{total}).")
    print(f"Active steward present: {active_label}")


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    require_active_steward: bool = False,
    verbose: bool = True,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Create or check the FabricOps metadata tables for one environment.

    Creates missing metadata tables, additively evolves existing metadata
    tables with missing canonical columns, and validates canonical column
    types against the registry for the installed FabricOps version. Existing
    data and extra physical columns are preserved; incompatible canonical
    types and known legacy schemas are reported as failures. Catalogue's
    ``load_strategy_parameters_json``, ``scheduled_refresh_json`` and
    ``profile_key_candidates_json`` retain their names but store native Spark
    structs. Supported historical strings are strictly validated and converted
    automatically in one conflict-checked Delta commit at the configured location.
    Rows, unrelated columns, audit values and table properties are preserved.
    The per-table evolved result records the pre-upgrade and committed versions.
    Blank strings become null; historical list-only candidates retain their order
    with null status and null maximum width. Repeated setup validates native
    values without rewriting them. Interrupted or unacknowledged commits can be
    recovered by rerunning setup. Recovery never automatically restores an older
    version over subsequent writes; see the Catalogue upgrade guidance.

    This function prepares the metadata table structures only. It does not
    create business metadata records such as stewards, agreements, catalogue
    rows, profiles, lineage events, enrichment records, guardrail rules, or
    guardrail results.

    Parameters
    ----------
    spark : Any
        Spark session used to create empty schema DataFrames and read or write
        the metadata lakehouse tables.
    config : FrameworkConfig | dict[str, Any]
        FabricOps configuration used to find the selected environment and its
        metadata lakehouse.
    env : str
        Environment whose configured metadata lakehouse should be initialized
        or validated.
    require_active_steward : bool, default=False
        When ``True``, raise if ``METADATA_DATA_STEWARD`` contains no active
        steward rows after setup. This option does not create a steward
        record.
    verbose : bool, default=True
        Controls whether the concise per-table setup summary is printed.
    raise_on_failure : bool, default=False
        When ``True``, raise a ``RuntimeError`` after processing all tables if
        any table failed creation or validation.

    Returns
    -------
    dict[str, Any]
        A dictionary summarizing the completed metadata lakehouse setup,
        including the resolved governance and engineering metadata schemas,
        metadata tables checked,
        tables created, additively evolved, successfully validated, failed tables,
        per-table messages, active steward readiness, fully qualified table
        names, and overall setup status. Key fields are ``status``,
        ``data_agreement``, ``governance``, ``engineering``, ``tables``,
        ``table_results``,
        ``metadata_schemas``, ``fully_qualified_tables``, ``created_tables``,
        ``evolved_tables``, ``validated_tables``, ``failed_tables``,
        ``created_or_checked_tables``,
        ``warnings``, ``active_metadata_tables``, and
        ``active_metadata_table_count``.

        ``status`` is ``"ready"`` when no table failures occur,
        ``"partial_failure"`` when some tables succeed and some fail, and
        ``"failed"`` when all table operations fail. ``data_agreement``
        summarizes steward, agreement, and contract readiness. ``governance``
        summarizes governance-authored tables, and ``engineering`` summarizes
        engineering-written tables. Active steward readiness depends on
        whether active steward rows already exist.

    Raises
    ------
    ValueError
        If the configuration is invalid, the resolved ``metadata`` target is
        not a schema-enabled lakehouse, or ``require_active_steward=True`` and
        no active steward rows exist after setup.
    RuntimeError
        If ``raise_on_failure=True`` and one or more metadata tables fail
        creation or validation after all tables have been processed.

    Maintainer Notes
    ----------------
    Setup flow:

    1. Validate the supplied FabricOps configuration.
    2. Find the metadata lakehouse configured for the selected environment.
    3. Verify that the metadata target is a lakehouse.
    4. Resolve each table's physical schema from its canonical ownership and
       the configured governance/engineering schema names.
    5. Load the required FabricOps table definitions.
    6. Attempt to read each required metadata table.
    7. When a table is missing, create an empty Spark DataFrame using its
       required FabricOps table structure.
    8. Write that empty DataFrame to the metadata lakehouse using overwrite
       mode to create the table.
    9. Read the created table again.
    10. Validate overlapping canonical column names and physical Spark data types.
    11. Add missing canonical columns with an empty Delta append using
        ``mergeSchema=true``, then read and validate the table again.
    12. Continue processing the remaining tables when one table fails.
    13. Check whether at least one active steward record exists.
    14. Return overall, data-agreement, governance, and per-table setup
        results.

    ``data_agreement["active_steward_count"]`` is retained for compatibility
    and reports readiness presence: ``1`` when at least one active steward
    exists and ``0`` otherwise. It is not a complete active steward population
    count.

    The current metadata tables created or validated from
    ``metadata_table_schema_registry()`` are ``METADATA_DATA_STEWARD``,
    ``METADATA_DATA_AGREEMENT``, ``METADATA_DATA_CONTRACT``,
    ``METADATA_PIPELINE_REGISTRY``, ``METADATA_PIPELINE_RUN``,
    ``METADATA_DATA_CATALOGUE``, ``METADATA_DATA_PROFILED``,
    ``METADATA_DATA_PROFILED_FREQUENCY``, ``METADATA_DATA_LINEAGE``, ``METADATA_DATA_ACCESS``,
    ``METADATA_GUARDRAIL_RESULTS``, and ``METADATA_PROCESSING_STATE``.

    Of that inventory, ``METADATA_DATA_CATALOGUE``,
    ``METADATA_DATA_PROFILED``, ``METADATA_DATA_PROFILED_FREQUENCY``, and
    ``METADATA_DATA_LINEAGE`` are Live schemas with compatibility guarantees.
    Every other metadata schema in the registry remains Preview.

    Detailed table contents:

    - ``METADATA_DATA_STEWARD`` is a person registry storing ``steward_id``,
      ``steward_name``, ``steward_role``, ``contact``, ``is_active``,
      ``custom_fields_json``, and the standard audit fields. Responsibility
      effective periods remain on ``METADATA_DATA_AGREEMENT``.
    - ``METADATA_DATA_AGREEMENT`` stores ``agreement_id``,
      ``agreement_version``, ``agreement_name``, ``domain``,
      ``provider_steward_id``, ``recipient_steward_id``, ``recipient``,
      ``start_date``, ``expiry_date``, ``business_purpose``,
      ``custom_fields_json``, and the standard audit fields.
    - ``METADATA_DATA_CONTRACT`` stores one table-centric lifecycle version.
      A draft keeps its complete editable governed definition in
      ``contract_payload_json``, including descriptive Enrichment and executable
      Guardrails; each Save overwrites that draft JSON in place.
      Separate definition tables are neither required nor deleted by setup.
      Freezing changes the version to ``frozen`` and makes its JSON immutable.
      A later version is seeded from the previous frozen JSON. Activation keeps
      ``status='frozen'`` and uses ``is_active`` to identify the Production
      version while linking the exact Data Agreement version.
    - ``METADATA_DATA_CATALOGUE`` stores the current structural registry through
      ``metadata_level``, ``table_id``, ``column_id``, ``environment_name``,
      physical table context, ``column_name``, ``data_type``, profiling dates,
      activation state, and the standard audit fields.
    - ``METADATA_DATA_PROFILED`` stores ``profile_id``,
      ``profile_snapshot_id``, ``table_id``, ``column_id``,
      ``environment_name``, ``data_type``,
      ``row_count``, ``non_null_count``, ``null_count``, ``null_percent``,
      ``distinct_count``, ``distinct_percent``, ``mean_value``,
      ``stddev_value``, ``min_value``, ``percentile_25_value``,
      ``median_value``, ``percentile_75_value``, ``max_value``,
      and the standard audit fields.
    - ``METADATA_DATA_PROFILED_FREQUENCY`` stores frequency rows through
      ``frequency_id``, ``profile_id``, ``profile_snapshot_id``, value, count,
      percentage, rank, profiled row totals, and the standard audit fields.
    - ``METADATA_DATA_LINEAGE`` stores ``lineage_id``, canonical ``table_id``,
      ``environment_name``, ``pipeline_role``, and the
      standard audit fields.
    - ``METADATA_DATA_ACCESS`` stores access scope, role, permission,
      approval, expiry, table and column identity, and audit information.
    - ``METADATA_GUARDRAIL_RESULTS`` stores guardrail execution results,
      status, continuation decision, expected and actual values, result
      payload, and audit information.

    Standard audit fields are ``_committed_by``, ``_committed_at``,
    ``_workspace_id``, ``_workspace_name``, ``_notebook_id``,
    ``_notebook_name``, ``_metadata_lakehouse_name``, and ``_activity_id``.

    The Preview Processing State table is named ``METADATA_PROCESSING_STATE``.
    Retired Preview tables, including ``METADATA_SOURCE_OBSERVATION``, may
    remain physically present. Presence checks in both configured metadata
    schemas return advisory ``warnings`` with retirement versions and cleanup
    guidance; access/storage errors return diagnostics rather than absence.
    No historical rows are collected, migrated or deleted. Alerts never affect
    canonical readiness or ``raise_on_failure``. Only ``verbose=True`` prints
    alerts and underlying I/O messages. A fresh Processing State table does not
    establish progress for populated targets; reconcile retained progress or
    deliberately rebuild/replay targets before resuming incremental work.

    ``METADATA_PIPELINE_REGISTRY`` requires one native authority row.
    ``METADATA_PIPELINE_RUN`` requires native execution facts with exact table/contract references, bindings and operation modes.
    Old Registry/Run layouts and incomplete native layouts require explicit
    stopped-deployment reconciliation or a deliberate disposable Preview reset; setup never adds columns to reinterpret existing run history.

    Existing tables are validated by canonical column name and compatible
    Spark data type. Physical Spark/Delta nullability is intentionally not
    compared or migrated. Missing canonical columns are added automatically
    through an empty append with Delta ``mergeSchema=true``; existing rows and
    unrelated extra columns are preserved. Existing canonical columns with
    incompatible physical types still fail validation. The legacy
    ``frequency_json`` column specifically fails ``METADATA_DATA_PROFILED``
    validation because that normalized-frequency change requires explicit
    migration or recreation. Existing tables are never overwritten merely
    because their schema differs. Processing continues for remaining metadata
    tables, and ``raise_on_failure=True`` raises only after all tables have
    been processed when failures exist.

    Pipeline Registry is seeded with its native authority row using
    error-if-exists creation; repeat initialization validates the existing schema
    without replacing identity or approval history. A missing ordinary table is
    created by writing an empty Spark DataFrame with the
    required FabricOps table structure. This creates the metadata table structure but
    does not populate business metadata records. The function does not
    automatically create steward records, agreements, contracts, catalogue
    records, profile records, lineage events, access assignments, enrichment
    records, guardrail rules, or guardrail results; those are populated by
    their respective FabricOps workflows.

    """
    normalized = validate_framework_config(config)
    metadata_store = get_store(config=normalized, env=env, store="Metadata")
    if getattr(metadata_store, "kind", None) != "lakehouse":
        raise ValueError(f"Target '{env}/metadata' is not a lakehouse store.")
    if metadata_store.schema_enabled is not True:
        raise ValueError("FabricOps Metadata Lakehouse must be schema-enabled.")
    context = {"config": normalized, "env": env, "_fabricops_suppress_io_log": not verbose}
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
                    table_name, store="Metadata", schema=resolved_metadata_schema, spark_session=spark, context=context
                )
            except Exception as exc:
                if not is_table_not_found_error(exc):
                    raise RuntimeError(
                        f"Unable to read metadata table {table_name!r}. Original {type(exc).__name__}: {exc}"
                    ) from exc
                initial_rows = []
                if table_name == "METADATA_PIPELINE_REGISTRY":
                    from fabricops_kit.config.audit import build_runtime_audit_fields
                    from fabricops_kit.activated_pipeline.shared import empty_pipeline_authority
                    initial_rows = [{**empty_pipeline_authority(),
                                     **build_runtime_audit_fields(config=normalized, env=env, runtime_context=context)}]
                empty_frame = spark.createDataFrame(initial_rows, schema=schema)
                write_lakehouse_table(
                    empty_frame,
                    table_name,
                    store="Metadata",
                    schema=resolved_metadata_schema,
                    mode="errorifexists" if table_name in {"METADATA_PIPELINE_REGISTRY", "METADATA_PIPELINE_RUN", "METADATA_DATA_CATALOGUE"} else "overwrite",
                    verbose=False,
                    context=context,
                )
                created = True
                table = read_lakehouse_table(
                    table_name, store="Metadata", schema=resolved_metadata_schema, spark_session=spark, context=context
                )
            upgrade = None
            if table_name == "METADATA_DATA_CATALOGUE":
                table, upgrade = _upgrade_catalogue(
                    spark=spark, table=table, expected_schema=schema,
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
                        spark_session=spark,
                        context=context,
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
                    print(f"[{index}/{total_tables}] Created {table_name}\n")
            elif upgrade:
                evolved_tables.append(table_name)
                table_results[table_name] = {
                    **_result(table_name, "evolved", "Catalogue automatically upgraded to native nested types and verified."),
                    **upgrade,
                }
                if verbose:
                    print(f"[{index}/{total_tables}] Automatically upgraded {table_name} to native nested types\n")
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
                    print(f"[{index}/{total_tables}] Evolved {table_name}")
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
                print(f"[{index}/{total_tables}] Failed {table_name}")
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
