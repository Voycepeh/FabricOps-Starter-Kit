"""Public owner file for FabricOps metadata table setup."""

from __future__ import annotations

from fabricops_kit.io.shared import get_spark_session, read_delta_path, resolve_configured_lakehouse_table, write_delta_path, validate_metadata_primary_key, retry_delta_metadata

from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

from typing import Any

from .metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    METADATA_PRIMARY_KEYS,
    metadata_json_schema,
    decode_metadata_row,
    encode_metadata_row,
    parse_metadata_json,
    RETIRED_PREVIEW_METADATA_TABLES,
    HISTORICAL_METADATA_TABLES,
    RETIRED_METADATA_COLUMNS,
    PHYSICAL_WORKSPACE_COLUMNS,
    LEGACY_WORKSPACE_TABLES,
    GOVERNANCE_METADATA_TABLES,
    ENGINEERING_METADATA_TABLES,
    metadata_table_physical_schema,
    metadata_schema_type_name,
    metadata_table_field_names,
    metadata_table_schema_registry,
    migrate_asset_references,
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


def _historical_table_warnings(*, config, spark, context):
    """Report retained participation history without reading rows or changing it."""
    warnings = []
    for table, retirement in HISTORICAL_METADATA_TABLES.items():
        try:
            read_lakehouse_table(table, store="Metadata", schema=config.engineering_metadata_schema,
                                 context={**context, "_spark_session": spark})
        except Exception as exc:
            if not _retired_table_is_missing(exc):
                warnings.append(f"Unable to inspect historical {table}: {type(exc).__name__}. "
                                "Presence is unknown; existing data is untouched.")
        else:
            warnings.append(f"{table} is retained historical metadata. {retirement['guidance']} "
                            "Setup never creates, updates or deletes this table.")
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
    missing = sorted(set(expected) - set(existing))
    unexpected = sorted(set(existing) - set(expected))
    mismatches: list[str] = []
    for name in sorted(set(existing) & set(expected)):
        existing_field = existing[name]
        if existing_field is None:
            continue
        expected_type = metadata_schema_type_name(expected[name].dataType)
        existing_type = metadata_schema_type_name(existing_field.dataType)
        if existing_type != expected_type:
            mismatches.append(f"{name}: expected {expected_type}, found {existing_type}")

    differences = []
    if missing:
        differences.append("Missing columns: " + ", ".join(missing))
    if unexpected:
        differences.append("Unexpected columns: " + ", ".join(unexpected))
    if mismatches:
        differences.append("Type mismatches: " + "; ".join(mismatches))
    detail = ". ".join(differences)

    supported_asset_addition = (table_name == "METADATA_DATA_CONTRACT_ACTIVATION" and allow_missing
        and not unexpected and set(missing) <= {"asset_type"})
    if table_name in {"METADATA_PIPELINE_RUN", "METADATA_PIPELINE_REGISTRY", "METADATA_DATA_CONTRACT_ACTIVATION"} and (missing or unexpected) and not supported_asset_addition:
        raise ValueError(
            f"Incompatible {table_name} physical schema. {detail}. "
            "Existing data has been preserved; automatic schema evolution is unsafe for this layout. "
            "Inspect the differences and plan an explicit migration or reset."
        )
    if mismatches:
        raise ValueError(
            f"{table_name} physical schema does not match the canonical FabricOps metadata schema: {detail}."
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
    _, _, _, path = resolve_configured_lakehouse_table("Metadata", table_name, metadata_schema, context=context)
    retry_delta_metadata(lambda: write_delta_path(empty_frame, path, mode="append", options={"mergeSchema": "true"}))


def _enforce_metadata_primary_key(*, spark, table, table_name, metadata_schema, context):
    """Validate retained rows, then add required-key checks and Serializable isolation."""
    from delta.tables import DeltaTable

    validate_metadata_primary_key(table_name, table)
    _, _, _, path = resolve_configured_lakehouse_table("Metadata", table_name, metadata_schema, context=context)
    target = "delta.`" + path.replace("`", "``") + "`"
    properties = DeltaTable.forPath(spark, path).detail().select("properties").first()["properties"]
    if properties.get("delta.isolationLevel") != "Serializable":
        spark.sql(f"ALTER TABLE {target} SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')")
    constraint = "fabricops_primary_key_required"
    check = " AND ".join(f"`{key}` IS NOT NULL AND length(trim(CAST(`{key}` AS STRING))) > 0"
                         for key in METADATA_PRIMARY_KEYS[table_name])
    existing = properties.get("delta.constraints." + constraint)
    if existing is None:
        spark.sql(f"ALTER TABLE {target} ADD CONSTRAINT {constraint} CHECK ({check})")
    else:
        parser = spark._jsparkSession.sessionState().sqlParser()
        if parser.parseExpression(existing).canonicalized().sql() != parser.parseExpression(check).canonicalized().sql():
            # Delta renders stored expressions with normalized parentheses/case.
            # Never silently replace a genuinely different existing constraint.
            raise ValueError(f"{table_name}: existing primary key constraint differs from the canonical key.")



_LEGACY_CATALOGUE_FIELDS = {"metadata_level", "column_id", "column_name", "data_type"}


def _migrate_catalogue_rows(rows, *, spark, convert, context):
    """Consolidate v0.5.0 TABLE/COLUMN rows using verified physical coordinates."""
    from fabricops_kit.config.shared import build_table_id, resolve_asset_workspace_name

    config = context["config"]
    parents = {}
    children = {}
    for row in rows:
        original = row.asDict(recursive=True)
        # v0.5.0 Catalogue registered TABLE parents and COLUMN children only.
        level = original.get("metadata_level")
        if level not in {"table", "column"}:
            raise ValueError(f"Catalogue has an invalid metadata_level {level!r}; inspect its legacy rows.")
        identity = original.get("table_id")
        workspace = original.get("workspace_id")
        kind = "TABLE"
        key = (workspace, identity, kind)
        if not all(isinstance(value, str) and value.strip() and value == value.strip() for value in key):
            raise ValueError(f"Catalogue has an invalid legacy asset identity {key!r}.")
        values = convert(row)
        if level == "column":
            column = {name: original.get(name) for name in ("column_id", "column_name", "data_type")}
            # Validate inactive definitions and duplicates before retiring them too.
            encode_metadata_row("METADATA_DATA_CATALOGUE", {"columns_json": [column]})
            children.setdefault(key, []).append((column, original.get("is_active") is not False))
        else:
            if key in parents or any(original.get(name) is not None for name in ("column_id", "column_name", "data_type")):
                raise ValueError(f"Catalogue has duplicate or conflicting parent rows for {key!r}.")
            parents[key] = values

    if orphans := children.keys() - parents.keys():
        raise ValueError(f"Catalogue columns have no matching parent asset: {sorted(orphans)!r}.")
    table_keys = {(workspace, identity) for workspace, identity, _kind in parents}
    known_locations = {}
    if table_keys:
        run_table = "METADATA_PIPELINE_RUN"
        try:
            runs = read_lakehouse_table(run_table, store="Metadata",
                schema=metadata_table_physical_schema(config, run_table),
                context={**context, "_spark_session": spark, "_fabricops_suppress_io_log": True})
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
        else:
            if {"operations", "workspace_id"}.issubset(runs.columns):
                for run in runs.select("workspace_id", "operations").toLocalIterator():
                    operations = parse_metadata_json(run["operations"], field="METADATA_PIPELINE_RUN.operations")
                    if not isinstance(operations, list):
                        raise ValueError("Released Pipeline Run operations must be a JSON array.")
                    for operation in operations:
                        operation = migrate_asset_references(operation)
                        key = (run["workspace_id"], operation.get("table_id"))
                        if (key not in table_keys or operation.get("asset_type") == "FILE"
                                or operation.get("status") != "succeeded"):
                            continue
                        binding = migrate_asset_references(operation.get("destination") or {})
                        workspace, item = operation.get("asset_workspace_id"), binding.get("item_id")
                        if workspace and item:
                            known_locations.setdefault(key, set()).add((workspace.lower(), item.lower()))
    resolved = set()
    names = {}
    for (workspace, identity, kind), parent in parents.items():
        key = (workspace, identity, kind)
        columns = children.get(key, [])
        definitions = [column for column, _ in columns]
        encode_metadata_row("METADATA_DATA_CATALOGUE", {"columns_json": definitions})
        active = sorted((column for column, is_active in columns if is_active), key=lambda column: column["column_name"])
        observed = active if columns or parent.get("last_profiled_at") else None
        layer = parent.get("layer")
        try:
            store = get_store(config, workspace, layer)
            configured_location = (store.workspace_id.lower(), store.item_id.lower())
            recorded_locations = known_locations.get((workspace, identity), set())
            if not recorded_locations and not parent.get("item_id"):
                raise ValueError("The legacy row has neither a retained item ID nor a successful Run binding.")
            if (store.kind != parent.get("store_type")
                    or (parent.get("item_id") and parent["item_id"].lower() != configured_location[1])
                    or (recorded_locations and recorded_locations != {configured_location})
                    or not parent.get("table_name")
                    or build_table_id(store.kind, layer, parent.get("schema_name"), parent["table_name"]) != identity):
                raise ValueError("Stored coordinates disagree with the configured store or Table ID.")
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Cannot establish the physical workspace for legacy Catalogue TABLE {key!r}, store {layer!r}. "
                f"{exc} Verify the original configuration-scope FabricStore mapping, stored coordinates and retained Pipeline Run destinations."
            ) from exc
        workspace = store.workspace_id.lower()
        parent["item_id"] = parent.get("item_id") or store.item_id
        new_key = (workspace.lower(), identity, kind)
        if new_key in resolved:
            raise ValueError(f"Legacy Catalogue assets resolve to the same physical identity {new_key!r}.")
        resolved.add(new_key)
        if workspace not in names:
            names[workspace] = resolve_asset_workspace_name(workspace, context=context)
        parent.update(asset_workspace_id=workspace, asset_workspace_name=names[workspace], asset_type=kind, columns_json=observed)
        replacement = encode_metadata_row("METADATA_DATA_CATALOGUE", parent)
        if decode_metadata_row("METADATA_DATA_CATALOGUE", replacement)["columns_json"] != observed:
            raise ValueError(f"Catalogue schema verification failed for {new_key!r}.")
        yield replacement


def _upgrade_metadata_table(*, spark, table, table_name, expected_schema, metadata_schema, context):
    """Upgrade v0.5.0 identities and Catalogue rows atomically.

    Schema and replacement files commit together. Whole-table read tracking and
    metadata conflict checks prevent loss of concurrent updates/blind appends.
    Both released and current JSON fields are STRING; no intermediate native
    collection schema is converted. Retained JSON keeps its exact bytes.
    """
    import json
    from uuid import uuid4

    from fabricops_kit.io.shared import resolve_configured_lakehouse_table

    catalogue = table_name == "METADATA_DATA_CATALOGUE"
    retirements = dict(RETIRED_METADATA_COLUMNS.get(table_name, {}))
    if catalogue:
        retirements.update(dict.fromkeys(_LEGACY_CATALOGUE_FIELDS))
    renames = PHYSICAL_WORKSPACE_COLUMNS.get(table_name, {})
    if table_name in LEGACY_WORKSPACE_TABLES:
        renames = {"workspace_id": "legacy_workspace_id"}
    retirements.update(renames)
    retired = set(_table_column_names(table)) & set(retirements)
    if not hasattr(table, "schema"):
        if retired:
            raise ValueError(f"{table_name}: cannot verify retired column(s): {', '.join(sorted(retired))}; existing data preserved.")
        return table, None
    logical_fields = metadata_json_schema(table_name)
    if not logical_fields and not retired:
        return table, None
    expected = _schema_fields_by_name(expected_schema)
    if set(retirements) & set(expected):
        raise ValueError(f"Unsafe column retirement declaration for {table_name}.")

    def inspect(frame):
        from pyspark.sql.types import StructField

        physical_names = set(_table_column_names(frame))
        for old, new in renames.items():
            if old in physical_names and (new in physical_names
                    or table_name in LEGACY_WORKSPACE_TABLES and "asset_workspace_id" in physical_names):
                raise ValueError(f"{table_name} contains both {old} and {new}; existing data preserved.")

        compatible = frame.schema.__class__([
            StructField(renames[f.name], f.dataType, f.nullable, f.metadata) if f.name in renames else f
            for f in frame.schema.fields if f.name not in retirements or f.name in renames
        ])
        _validate_existing_metadata_schema(table_name, compatible, expected_schema, allow_missing=True)

    def convert(row):
        values = row.asDict(recursive=True)
        has_legacy_workspace = "workspace_id" in values
        if table_name in {"METADATA_DATA_CONTRACT", "METADATA_DATA_CONTRACT_ACTIVATION", "METADATA_GUARDRAIL_RESULTS"}:
            old_source = values.get("source_id")
            if old_source:
                if values.get("table_id") not in (None, old_source):
                    raise ValueError(f"{table_name}: conflicting asset identities; existing data preserved.")
                values.update(table_id=old_source, asset_type="FILE")
            elif "source_id" in values and values.get("table_id"):
                values["asset_type"] = "TABLE"
        if table_name in {"METADATA_DATA_CONTRACT", "METADATA_DATA_CONTRACT_ACTIVATION"}:
            values = migrate_asset_references(values)
        for old, new in renames.items():
            if old in values:
                values[new] = values.pop(old)
        if table_name in {"METADATA_DATA_PROFILED", "METADATA_DATA_PROFILED_FREQUENCY"} and has_legacy_workspace:
            values["asset_type"] = "TABLE"
        if table_name == "METADATA_DATA_CONTRACT_ACTIVATION" and has_legacy_workspace:
            destination = migrate_asset_references(parse_metadata_json(values["destination_json"], field="destination_json"))
            workspace = str(values.get("asset_workspace_id") or "").casefold()
            if not workspace or not isinstance(destination, dict) or workspace != str(destination.get("asset_workspace_id") or "").casefold():
                raise ValueError("Contract Activation workspace conflicts with its retained physical destination.")
        decoded = decode_metadata_row(table_name, values)
        if table_name == "METADATA_PIPELINE_RUN":
            from fabricops_kit.pipeline.shared import validate_pipeline_run
            validate_pipeline_run(decoded)
            for field in expected_schema.fields:
                if not field.nullable and decoded.get(field.name) is None:
                    raise ValueError(f"{table_name}.{field.name} cannot be null.")
        return encode_metadata_row(table_name, values)

    def validate(frame):
        if not logical_fields:
            return
        has_rows = False
        catalogue_keys = set()
        legacy_catalogue = catalogue and bool(set(_table_column_names(frame)) & _LEGACY_CATALOGUE_FIELDS)
        for row in frame.toLocalIterator():
            has_rows = True
            converted = convert(row)
            if catalogue and not legacy_catalogue:
                key = tuple(converted.get(name) for name in ("asset_workspace_id", "table_id", "asset_type"))
                if (not all(isinstance(value, str) and value.strip() and value == value.strip() for value in key)
                        or key[2] not in {"TABLE", "FILE"} or not str(converted.get("asset_workspace_name") or "").strip()):
                    raise ValueError(f"Catalogue has an incomplete physical asset identity {key!r}.")
                key = (key[0].lower(), *key[1:])
                if key in catalogue_keys:
                    raise ValueError(f"Catalogue has duplicate physical asset identity {key!r}.")
                catalogue_keys.add(key)
        if has_rows and table_name == "METADATA_PIPELINE_RUN" and frame.groupBy("run_id").count().where("count > 1").limit(1).count():
            raise ValueError("Duplicate Pipeline Run identities; existing history is preserved and schema evolution is blocked.")

    inspect(table)
    validate(table)
    if not retired:
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
    inspect(source)
    validate(source)
    actual = _schema_fields_by_name(source.schema)
    retired = set(actual) & set(retirements)
    if not retired:
        return source, None
    metadata = json.loads(txn.metadata().json())
    physical_schema = StructType.fromJson(json.loads(metadata["metaData"]["schemaString"]))
    legacy_catalogue = catalogue and bool(retired & _LEGACY_CATALOGUE_FIELDS)
    if legacy_catalogue and "metadata_level" not in retired:
        raise ValueError("Catalogue has an incomplete legacy layout without metadata_level; existing data preserved.")
    if retired:
        properties = metadata["metaData"].get("configuration", {})
        if (retired & set(metadata["metaData"].get("partitionColumns", []))
                or properties.get("delta.columnMapping.mode", "none") != "none"
                or any(key.startswith("delta.constraints.") for key in properties)
                or any("delta.generationExpression" in field.metadata for field in physical_schema)):
            raise ValueError(f"{table_name}: retired columns require an unsupported partition, mapping or constraint migration; existing data preserved.")
        for name in sorted(retired - set(renames) - (_LEGACY_CATALOGUE_FIELDS if legacy_catalogue else set())):
            replacement_name = retirements[name]
            column = F.col('`' + name.replace('`', '``') + '`')
            safe = column.isNull()
            if replacement_name is not None:
                if replacement_name not in actual or actual[name].dataType != actual[replacement_name].dataType:
                    raise ValueError(f"{table_name}.{name}: replacement type is incompatible; existing data preserved.")
                safe = safe | column.eqNullSafe(F.col(replacement_name))
                if name == "source_id":
                    # convert() fills the common identity inside this same Delta
                    # transaction; conflicting populated identities remain blocked.
                    safe = safe | (F.col(replacement_name).isNull() & (F.length(F.trim(column)) > 0))
            if source.where(~safe).limit(1).count():
                raise ValueError(f"{table_name}.{name}: populated retired column is not provably redundant; existing data preserved.")
    def replacement_schema(schema):
        retained = [
            StructField(renames[f.name], f.dataType, f.nullable or renames[f.name] == "legacy_workspace_id", f.metadata) if f.name in renames
            else f
            for f in schema.fields if f.name not in retired or f.name in renames
        ]
        present = {f.name for f in retained}
        return StructType(retained + [
            StructField(f.name, f.dataType, True, f.metadata) for f in expected_schema.fields if f.name not in present
        ])

    target_schema = replacement_schema(source.schema)
    stage = path.rstrip("/") + "_metadata_upgrade_staging/" + str(uuid4())
    fs_path = jvm.org.apache.hadoop.fs.Path(stage)
    fs = fs_path.getFileSystem(spark._jsc.hadoopConfiguration())
    try:
        retained_names = target_schema.fieldNames()
        if legacy_catalogue:
            rows = _migrate_catalogue_rows(source.toLocalIterator(), spark=spark, convert=convert, context=context)
            data = [{name: row.get(name) for name in retained_names} for row in rows]
        else:
            data = source.rdd.map(convert).map(lambda row: {name: row.get(name) for name in retained_names})
        replacement = spark.createDataFrame(data, target_schema)
        replacement.write.mode("errorifexists").parquet(stage)
        replacement = spark.read.schema(target_schema).parquet(stage)
        if legacy_catalogue:
            validate(replacement)
        replacement_metadata_schema = replacement_schema(physical_schema)
        metadata["metaData"]["schemaString"] = replacement_metadata_schema.json()
        txn.updateMetadata(delta.actions.Action.fromJson(json.dumps(metadata)), False)
        added = txn.writeFiles(replacement._jdf)
        actions = jvm.java.util.ArrayList()
        for index in range(files.size()):
            actions.add(files.apply(index).remove())
        for index in range(added.size()):
            actions.add(added.apply(index))
        seq = jvm.scala.collection.JavaConverters.asScalaBufferConverter(actions).asScala().toSeq()
        recovery = json.dumps({"fabricops_metadata_upgrade": 1, "removed_columns": sorted(retired), "table": table_name, "pre_upgrade_version": version})
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
        if committed.schema != target_schema:
            raise RuntimeError(f"{table_name} upgrade committed but schema verification failed; inspect Delta history (pre-upgrade version {version}, committed version {committed_version}).")

        def serialized(frame):
            return frame.select(F.to_json(F.struct(*[F.col('`' + name.replace('`', '``') + '`')
                for name in frame.columns]), options={"ignoreNullFields": "false", "timeZone": "UTC",
                    "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                    "timestampNTZFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"}).alias("row"))

        before, after = serialized(replacement), serialized(committed)
        if before.exceptAll(after).limit(1).count() or after.exceptAll(before).limit(1).count():
            raise RuntimeError(f"{table_name} upgrade committed but data verification failed; inspect Delta history (pre-upgrade version {version}, committed version {committed_version}).")
        return spark.read.format("delta").load(path), {
            "pre_upgrade_version": version, "upgrade_version": committed_version,
            **({"recovery_guidance": f"Pause metadata writers and inspect Delta history. To revert, use "
                 f"RESTORE TABLE delta.`{path}` TO VERSION AS OF {version} after checking for later writes."}
               if legacy_catalogue or retired & set(renames) or "source_id" in retired else {}),
            "converted_columns": [], "removed_columns": sorted(retired),
            "added_columns": [f.name for f in expected_schema.fields if f.name not in actual],
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


def _setup_processing_state(*, spark: Any, context: dict[str, Any]) -> dict[str, Any]:
    """Create or validate operational state without changing existing progress."""
    from fabricops_kit.pipeline.shared import (
        PROCESSING_STATE_SCHEMA,
        PROCESSING_STATE_TABLE,
        processing_state_path,
        processing_state_schema,
        validate_processing_state_isolation,
        validate_processing_state_schema,
    )

    path = processing_state_path(context)
    status = "validated"
    try:
        state = read_delta_path(spark, path)
    except Exception as exc:
        get_condition = getattr(exc, "getCondition", None) or getattr(exc, "getErrorClass", None)
        if not callable(get_condition) or get_condition() not in {"PATH_NOT_FOUND", "DELTA_PATH_DOES_NOT_EXIST"}:
            raise
        empty = spark.createDataFrame([], processing_state_schema())
        write_delta_path(empty, path, mode="errorifexists", options={"delta.isolationLevel": "Serializable"})
        state = read_delta_path(spark, path)
        status = "created"
    validate_processing_state_schema(state.schema)
    from delta.tables import DeltaTable

    validate_processing_state_isolation(DeltaTable.forPath(spark, path))
    return {"status": status, "path": f"Tables/{PROCESSING_STATE_SCHEMA}/{PROCESSING_STATE_TABLE}"}


def setup_metadata_tables(
    *,
    config: FrameworkConfig | dict[str, Any],
    workspace_id: str,
    require_active_steward: bool = False,
    verbose: bool = True,
    raise_on_failure: bool = False,
) -> dict[str, Any]:
    """Create, validate and safely evolve the 13 canonical metadata tables.

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
        readiness, a separate processing_state result, and advisory diagnostics for
        noncanonical metadata tables. Overall readiness includes Processing State.

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
    and Contract Activation use Serializable isolation. Processing State is
    initialized at misc.PROCESSING_STATE in the configured Metadata Lakehouse,
    separately from the canonical METADATA_* tables. Its schema and Serializable
    isolation are validated on repeat setup; existing rows are preserved.
    Setup never manufactures
    approvals, populates business metadata or replaces business targets. Governance definitions and activation are independent workflows.

    Compatible missing columns are added automatically. Only columns explicitly
    declared for retirement are removed, following their table-specific validation. Other extension
    columns are preserved where the table's identity contract permits them.
    Operational file source_id values are copied into the common table_id and
    validated before source_id is retired. Conflicting identities block migration.
    v0.5.0 profile rows are TABLE observations; their workspace remains explicitly
    historical when physical scope cannot be established. Stop pipelines for this schema migration; recovery
    restores the returned pre-upgrade Delta version together with the prior code.
    Unproven populated retirements fail with data preserved. Cleanup and supported
    identity changes commit atomically, with the pre-upgrade Delta version
    returned for recovery before VACUUM or further writes. Setup never vacuums.
    For legacy Catalogue rows, setup validates parent and column identities,
    resolves physical workspaces, preserves stored column IDs in columns_json,
    and retires the separate column records in the same Delta commit.
    Setup standardizes physical asset workspace columns when their scope is known.
    Historical workspace values without sufficient proof remain in legacy_workspace_id
    extension columns on upgraded tables only; fresh tables omit this column.
    Contract activation destinations and notebook audit fields retain their original values.
    The per-table result returns the pre-upgrade version and recovery command.
    Migration starts at released v0.5.0 and ends at the current canonical schema.
    Older and intermediate PR schemas have no conversion paths. Catalogue and
    Pipeline Run collection fields remain validated JSON strings; native physical
    collections are rejected. Identity changes use tracked Delta reads and exact
    schema/data readback. Existing rows, audit values, extension fields, table
    identity/properties and Delta transaction identities are preserved. Run
    provenance fields and retained content hashes are preserved.
    Repeated setup validates compliant tables without rewriting them.

    Processing State observations, checkpoints, accepted baselines and publication
    receipts remain intact. Missing progress is never inferred for populated
    targets. Incompatible identity layouts, incorrect types, malformed JSON and
    duplicate Run identities fail explicitly with the existing data preserved.
    A failure in one table does not prevent validation of the remaining tables.
    Unchanged fields retain their physical nullability and order. Renamed
    legacy_workspace_id extension fields are nullable so new physical observations can omit them.

    Governed admission remains blocked pending signed-in Fabric acceptance.
    Retirement presence diagnostics are advisory; unsupported tables are never
    read as canonical authority or automatically deleted. METADATA_DATA_LINEAGE
    stores scalar column dependency facts projected from finalized Runs. Setup
    additively adds the new nullable fields to retained activity layouts without
    rewriting historical rows; lineage_version=1 identifies new facts. Participation
    remains in METADATA_PIPELINE_RUN.operations.

    Primary keys shown in the metadata diagram are validated for every table.
    Setup rejects existing null, blank or duplicate keys without deleting rows,
    enables Serializable isolation and installs required-key Delta constraints.
    Uniqueness is enforced by FabricOps transactional writers; external writers
    must use the same protocol. Re-run setup before using upgraded writers.

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
    warnings.extend(_historical_table_warnings(config=normalized, spark=spark, context=context))

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
                    options={"delta.isolationLevel": "Serializable"},
                )
                created = True
                table = read_lakehouse_table(
                    table_name, store="Metadata", schema=resolved_metadata_schema, context={**(context or {}), "_spark_session": spark}
                )
            upgrade = None
            if not created and hasattr(table, "schema") and table_name in {"METADATA_PIPELINE_REGISTRY", "METADATA_PIPELINE_ACTIVATION"}:
                _validate_existing_metadata_schema(table_name, table.schema, schema)
            if (metadata_json_schema(table_name) or RETIRED_METADATA_COLUMNS.get(table_name)
                    or table_name in PHYSICAL_WORKSPACE_COLUMNS or table_name in LEGACY_WORKSPACE_TABLES):
                table, upgrade = _upgrade_metadata_table(
                    spark=spark, table=table, table_name=table_name, expected_schema=schema,
                    metadata_schema=resolved_metadata_schema, context=context)
            evolved_columns: list[str] = []
            if not created:
                columns = _table_column_names(table)
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
            _enforce_metadata_primary_key(spark=spark, table=table, table_name=table_name,
                metadata_schema=resolved_metadata_schema, context=context)
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
                    **_result(table_name, "evolved", "Metadata schema automatically upgraded and verified."),
                    **upgrade,
                }
                if verbose:
                    print(f"[{index:,}/{total_tables:,}] Automatically upgraded {table_name}\n")
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
    try:
        processing_state = _setup_processing_state(spark=spark, context=context)
        if verbose and processing_state["status"] == "created":
            print(f"Processing State: {processing_state['status']} (misc.PROCESSING_STATE)")
    except Exception as exc:
        processing_state = {"status": "failed", "path": "Tables/misc/PROCESSING_STATE",
                            "message": f"{type(exc).__name__}: {exc}"}
        if verbose:
            print(f"Processing State failed: {processing_state['message']}")
    state_failed = processing_state["status"] == "failed"
    status = "ready" if not failed_tables and not state_failed else ("partial_failure" if successful else "failed")
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
        "processing_state": processing_state,
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
    if raise_on_failure and (failed_tables or state_failed):
        detail = "; ".join(f"{table}: {table_results[table]['message']}" for table in failed_tables)
        if state_failed:
            detail = "; ".join(filter(None, [detail, f"misc.PROCESSING_STATE: {processing_state['message']}"]))
        raise RuntimeError(f"FabricOps metadata setup failed for {len(failed_tables) + int(state_failed)} table(s): {detail}")
    return result


__all__ = ["setup_metadata_tables"]
