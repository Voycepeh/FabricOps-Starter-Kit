"""Public orchestrator for the disposable FabricOps Guided Demo environment."""

from __future__ import annotations
from contextlib import ExitStack
from types import SimpleNamespace
from fabricops_kit.activated_pipeline.shared import FabricNotebookClient
from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import (
    read_lakehouse_csv,
    read_lakehouse_table,
    read_warehouse_query,
    read_warehouse_table,
    write_lakehouse_table,
    write_warehouse_table,
)
from fabricops_kit.io.shared import (
    get_spark_session,
    resolve_configured_lakehouse_table,
)
from fabricops_kit.pipeline.shared import (
    PROCESSING_STATE_SCHEMA,
    PROCESSING_STATE_TABLE,
    processing_state_path,
    read_processing_state,
    resolve_physical_table_identity,
    validate_processing_state_schema,
)

_DEMO_PROCESSING_STATE = f"{PROCESSING_STATE_SCHEMA}.{PROCESSING_STATE_TABLE}"
_DEMO_RESET_METADATA = (
    _DEMO_PROCESSING_STATE,
    "METADATA_DATA_PROFILED_FREQUENCY",
    "METADATA_DATA_PROFILED",
)

_DEMO_SOURCES = {
    ("Bronze", "orders"): ("demo/orders.csv", 120),
    ("Bronze", "products"): ("demo/products.csv", 8),
    ("Gold", "order_history"): ("demo/order_history.csv", 180),
    ("Bronze", "inventory_movements"): ("demo/inventory_day1.csv", 8),
    ("Bronze", "product_master_updates"): ("demo/products_day1.csv", 8),
}
_DEMO_OUTPUTS = (
    ("Silver", "curated_orders"),
    ("Gold", "customer_summary"),
    ("Silver", "inventory_movements_append_all"),
    ("Silver", "inventory_movements_append_new_only"),
    ("Silver", "product_master_scd1"),
    ("Silver", "product_master_scd2"),
)
_DEMO_REMOVALS = (*_DEMO_OUTPUTS, ("Bronze", "orders"))


def _demo_reset_scope(_state):
    """Resolve exact demo identities only for stores pointing at the reset destinations."""
    from fabricops_kit.data_contract.shared import file_source_identity

    _state._demo_execution_scope = {}
    _state._demo_asset_scope = {}
    for workspace, stores in _state._demo_config.path_config.paths.items():
        ids = set()
        for store, table in (*_DEMO_SOURCES, *_DEMO_OUTPUTS):
            selected = _state.context.paths[store]
            mapped = stores.get(store)
            if mapped is None or (mapped.workspace_id, mapped.item_id) != (selected.workspace_id, selected.item_id):
                continue
            table_id = resolve_physical_table_identity(
                _state._demo_config, workspace, store=store, schema="demo", table_name=table,
            )["table_id"]
            ids.add(table_id)
            _state._demo_asset_scope.setdefault(selected.workspace_id.lower(), set()).add(table_id)
        if ids:
            _state._demo_execution_scope[workspace.lower()] = ids
    # File selectors are retained, but their observations must not survive a data reset.
    bronze = _state.context.paths["Bronze"]
    files = {
        file_source_identity(asset_workspace_id=bronze.workspace_id, item_id=bronze.item_id,
            relative_path=f"demo/orders.{extension}", file_format=kind)["table_id"]
        for extension, kind in (("csv", "csv"), ("json", "json"), ("parquet", "parquet"), ("xlsx", "excel"))
    }
    _state._demo_asset_scope.setdefault(bronze.workspace_id.lower(), set()).update(files)
    for workspace, stores in _state._demo_config.path_config.paths.items():
        mapped = stores.get("Bronze")
        if mapped and (mapped.workspace_id, mapped.item_id) == (bronze.workspace_id, bronze.item_id):
            _state._demo_execution_scope.setdefault(workspace.lower(), set()).update(files)


def _demo_metadata_predicate(_state, table, *, boundary=False):
    """Build one Spark predicate reused for preview, deletion and verification."""
    from pyspark.sql import functions as F

    result = F.lit(False)
    processing = table == _DEMO_PROCESSING_STATE
    scopes = _state._demo_execution_scope if processing else _state._demo_asset_scope
    for workspace, ids in scopes.items():
        if processing:
            source = F.coalesce(F.col("source_table_id"), F.lit(""))
            target = F.coalesce(F.col("target_table_id"), F.lit(""))
            matches = source.isin(sorted(ids)) | target.isin(sorted(ids))
            if boundary:
                matches = matches & ((~source.isin(sorted(ids)) & (source != "")) |
                                     (~target.isin(sorted(ids)) & (target != "")))
            workspace_column = "workspace_id"
        else:
            matches = F.col("table_id").isin(sorted(ids))
            workspace_column = "asset_workspace_id"
        result = result | ((F.lower(F.col(workspace_column)) == workspace) & matches)
    return result


def _demo_metadata_frame(_state, table):
    """Read only metadata that the data reset may mutate, through configured routing."""
    if table == _DEMO_PROCESSING_STATE:
        frame = read_processing_state(context=_state._demo_runtime)
        validate_processing_state_schema(frame.schema)
    else:
        schema = metadata_table_physical_schema(_state._demo_config, table)
        frame = read_lakehouse_table(table, store="Metadata", schema=schema, context=_state._demo_runtime)
        expected = metadata_table_schema_registry()[table]
        actual = {field.name: field.dataType.simpleString() for field in frame.schema}
        incompatible = [field.name for field in expected if actual.get(field.name) != field.dataType.simpleString()]
        if incompatible:
            raise RuntimeError(
                f"{table} has missing columns or incompatible types: {', '.join(incompatible)}. "
                "Run the installed package metadata setup in the demo lakehouse, then restart 00C."
            )
    return frame


def _demo_metadata_counts(_state):
    """Count only matching demo progress and profile snapshots; history is retained."""
    return {table: _demo_metadata_frame(_state, table).where(_demo_metadata_predicate(_state, table)).count()
            for table in _DEMO_RESET_METADATA}


def _demo_check_processing_boundary(_state):
    """Refuse to reset a demo source/target shared with a non-demo publication."""
    rows = (_demo_metadata_frame(_state, _DEMO_PROCESSING_STATE)
        .where(_demo_metadata_predicate(_state, _DEMO_PROCESSING_STATE, boundary=True))
        .select("record_id", "workspace_id", "source_table_id", "target_table_id").limit(1).collect())
    if rows:
        row = rows[0]
        raise RuntimeError(
            f"Demo reset blocked by shared processing record {row['record_id']!r} in workspace "
            f"{row['workspace_id']!r}: {row['source_table_id']!r} -> {row['target_table_id']!r}. "
            "A demo table participates in a non-demo publication. Separate those business tables before resetting; "
            "no data has been changed."
        )


def _demo_assert_source(_state, actual, expected):
    """Compare full row multisets after normalizing Warehouse connector data types."""
    from pyspark.sql import functions as F

    actual = actual.select(*[F.col(field.name).cast(field.dataType).alias(field.name) for field in expected.schema])
    if actual.exceptAll(expected).limit(1).count() or expected.exceptAll(actual).limit(1).count():
        raise RuntimeError("Day 1 source verification failed: persisted content differs from the fixture. Rerun 00C.")


def _demo_gold_output_exists() -> bool:
    """Check only the configured demo Warehouse output using read-only SQL."""
    return bool(read_warehouse_query(
        "SELECT COUNT(*) AS n FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id "
        "WHERE s.name='demo' AND t.name='customer_summary'",
        store="Gold",
    ).first()["n"])


def _demo_prepare_gold_empty_output():
    """Preflight the exact demo Warehouse target without reading its rows."""
    if not _demo_gold_output_exists():
        return None
    existing = read_warehouse_table(store="Gold", schema="demo", table_name="customer_summary")
    if not getattr(existing, "columns", None):
        raise RuntimeError("Gold.demo.customer_summary has no readable columns; reset blocked.")
    return existing.limit(0)


def _demo_clear_gold_output(_state):
    """Clear rows through the configured Spark Warehouse writer, retaining an output table."""
    empty = _state._demo_gold_empty_output
    if empty is None:
        return  # Missing on repeat reset: no DDL, no table creation.
    write_warehouse_table(
        empty, store="Gold", schema="demo", table_name="customer_summary", mode="overwrite"
    )


def _demo_remove_outputs(_state, *, preview=False):
    """Remove exact configured output objects and their physical publication markers."""
    import notebookutils

    for store, table in _DEMO_REMOVALS:
        if store == "Gold":
            if preview:
                continue
            _demo_clear_gold_output(_state)
        else:
            _, _, _, path = resolve_configured_lakehouse_table(store, table, "demo")
            catalog = _state._demo_bronze_catalog if store == "Bronze" else _state._demo_silver_catalog
            qualified = f"{catalog}.`{table}`"
            if _state.spark.catalog.tableExists(qualified):
                location_rows = (
                    _state.spark.sql(f"DESCRIBE TABLE EXTENDED {qualified}").where("col_name = 'Location'").collect()
                )
                if len(location_rows) != 1 or location_rows[0]["data_type"].rstrip("/") != path.rstrip("/"):
                    raise RuntimeError(f"Catalog location mismatch for {store}.demo.{table}; reset blocked.")
                if not preview:
                    _state.spark.sql(f"DROP TABLE {qualified}")
            if not preview and notebookutils.fs.exists(path) and (not notebookutils.fs.rm(path, True)):
                raise RuntimeError(f"Could not remove {store}.demo.{table}; check permissions and retry 00C.")
        if not preview:
            action = "Cleared rows (missing is OK)" if store == "Gold" else "Removed output (missing is OK)"
            print(f"{action}: {store}.demo.{table}")


def _demo_verify_outputs(_state):
    """Verify that the Gold output is empty and the Lakehouse outputs are absent."""
    import notebookutils

    for store, table in _DEMO_REMOVALS:
        if store == "Gold":
            if _demo_gold_output_exists():
                rows = read_warehouse_query(
                    "SELECT COUNT_BIG(*) AS n FROM [demo].[customer_summary]",
                    store="Gold",
                ).first()["n"]
                if rows:
                    raise RuntimeError(
                        "Reset incomplete: Gold.demo.customer_summary still has rows. "
                        "Check Warehouse overwrite support and rerun 00C."
                    )
                if _state._demo_gold_empty_output is not None:
                    restored = read_warehouse_table(store="Gold", schema="demo", table_name="customer_summary")
                    if restored.schema != _state._demo_gold_empty_output.schema:
                        raise RuntimeError("Gold.demo.customer_summary schema changed during reset.")
            continue
        _, _, _, path = resolve_configured_lakehouse_table(store, table, "demo")
        exists = notebookutils.fs.exists(path) or _state.spark.catalog.tableExists(
            f"{_state._demo_bronze_catalog if store == 'Bronze' else _state._demo_silver_catalog}.`{table}`"
        )
        if exists:
            raise RuntimeError(f"Reset incomplete: {store}.demo.{table} remains. Check permissions and rerun 00C.")


def _demo_clear_metadata(_state, counts):
    """Delete only exact demo progress and profiles, retaining all other metadata."""
    from delta.tables import DeltaTable

    for _table in _DEMO_RESET_METADATA:
        if _table == _DEMO_PROCESSING_STATE:
            _path = processing_state_path(_state._demo_runtime)
        else:
            _, _, _, _path = resolve_configured_lakehouse_table(
                "Metadata", _table, metadata_table_physical_schema(_state._demo_config, _table),
                context=_state._demo_runtime,
            )
        _removed = 0
        if counts[_table]:
            _delta = DeltaTable.forPath(_state.spark, _path)
            _delta.delete(_demo_metadata_predicate(_state, _table))
            _removed = int(_delta.history(1).first()["operationMetrics"]["numDeletedRows"])
        print(f"{_table}: removed {_removed}")


def orchestrate_demo_reset(*, reset: bool = False) -> None:
    """Preview or reset the Guided Demo data and its processing progress to Day 1.

    Call after ``setup_notebook()``. Stop all executions and schedules using the
    reserved demo business tables, including promoted copies, and start fresh
    scenario notebook sessions after resetting. A dedicated demo environment
    is recommended; the Metadata Lakehouse need not be empty or demo-only.

    Parameters
    ----------
    reset : bool, default=False
        False prints configured destinations, scoped metadata counts and the
        eleven business tables without writing. True resets only those demo
        tables, their Processing State and profile snapshots after preflight.
        Only booleans are accepted.

    Returns
    -------
    None
        Prints actual removed counts and ``RESET COMPLETE`` after verification.

    Raises
    ------
    ValueError
        If reset is not a boolean.
    RuntimeError
        If setup, store mappings, required schemas, fixtures or catalog locations
        are invalid, a demo processing record links to a non-demo table, or
        verification fails. Fabric/Spark permission and transport errors propagate.

    Notes
    -----
    Deletion is restricted by exact demo identities and workspace: execution
    workspace for ``misc.PROCESSING_STATE`` and asset workspace for
    ``METADATA_DATA_PROFILED`` and ``METADATA_DATA_PROFILED_FREQUENCY``. Only
    configured mappings to the physical stores being reset participate. No
    nested Run or Contract payloads are inspected to authorize deletion.

    Contracts, activations, approvals, promotion history, Catalogue, Runs,
    Lineage, Guardrail results and saved submissions, Dry Runs and notebook
    snapshots are retained, including demo history. Profile snapshots for demo
    assets are discarded so standard profiling can run again. Historical grain
    and empty-frequency completion markers remain in retained Runs; use a zero
    profiling interval when those activities must run again immediately.
    This is a data restart, not a restart of governance authoring; use a separate
    environment for a fresh governance walkthrough.

    Four Day 1 source tables are overwritten. Orders CSV is validated and
    retained. Five Silver outputs and obsolete Bronze Orders are removed from
    the reserved ``demo`` schemas. Gold customer_summary is retained with zero
    rows when present. Other business tables and all source files are preserved.

    Preview never writes. Missing outputs and repeated resets are supported.
    The reset is not atomic across stores; after a partial failure stop writers,
    correct the cause and rerun. Never use it as production recovery. Actual
    Microsoft Fabric validation remains required.

    Examples
    --------
    >>> from fabricops_kit import setup_notebook, orchestrate_demo_reset
    >>> context = setup_notebook()
    >>> RESET_DEMO = False  # Preview before resetting demo data and progress.
    >>> orchestrate_demo_reset(reset=RESET_DEMO)

    """
    if type(reset) is not bool:
        raise ValueError("reset must be True or False.")
    config, workspace, runtime = resolve_fabric_context()
    setup = runtime.get("_notebook_setup", {}).get("result")
    if setup is None or setup.readiness_status != "ready" or setup.workspace_id != workspace:
        raise RuntimeError("Call setup_notebook() successfully before orchestrate_demo_reset().")
    missing = {"Metadata", "Bronze", "Silver", "Gold"} - set(setup.paths)
    if missing:
        raise RuntimeError(f"Required demo store mappings are missing: {sorted(missing)}. Check 00_env_config.")
    configured = config.path_config.paths.get(workspace, {})
    for key in ("Metadata", "Bronze", "Silver", "Gold"):
        mapped = configured.get(key)
        selected = setup.paths[key]
        if mapped is None or (mapped.workspace_id, mapped.item_id) != (selected.workspace_id, selected.item_id):
            raise RuntimeError(f"{key} mapping changed since notebook setup. Rerun setup_notebook() before resetting.")
    for key, kind in {"Bronze": "lakehouse", "Silver": "lakehouse", "Gold": "warehouse"}.items():
        store = setup.paths[key]
        if store.kind != kind or (kind == "lakehouse" and (not store.schema_enabled)):
            raise RuntimeError(f"Demo requires {key} to be a {kind} with the demo schema. Check 00_env_config.")
    _demo = SimpleNamespace(_demo_config=config, context=setup, _demo_runtime=runtime, spark=get_spark_session())
    _demo._metadata = _demo.context.paths["Metadata"]
    if _demo._metadata.kind != "lakehouse" or not _demo._metadata.schema_enabled:
        raise RuntimeError("Metadata must be a schema-enabled Lakehouse.")
    for _key in ("Metadata", "Bronze", "Silver", "Gold"):
        _store = _demo.context.paths[_key]
        print(f"{_key}: {_store.name} | workspace {_store.workspace_id} | item {_store.item_id}")
    _demo_reset_scope(_demo)
    _demo_counts = _demo_metadata_counts(_demo)
    for _table, _count in _demo_counts.items():
        print(f"{_table}: {_count} demo rows to remove")
    for _store, _table in _DEMO_SOURCES:
        if (_store, _table) != ("Bronze", "orders"):
            print(f"Restore Day 1: {_store}.demo.{_table}")
    print("Validate and retain Files/demo/orders.csv (120 rows); remove obsolete Bronze.demo.orders on full reset.")
    for _store, _table in _DEMO_OUTPUTS:
        print(f"Remove output: {_store}.demo.{_table}")
    print("Preserve Contracts, activations, Catalogue, Runs, Lineage, Guardrail results and saved lifecycle artifacts.")
    if not reset:
        print("Preview only. Stop demo executions and set reset=True to reset.")
        return
    _demo._demo_client = FabricNotebookClient()
    _item = _demo._demo_client.request(
        "GET", f"/workspaces/{_demo._metadata.workspace_id}/items/{_demo._metadata.item_id}"
    )
    # The configured item ID is authoritative; a display name is not proof of
    # demo ownership. Retain the independent scope and store-isolation checks.
    if _item.get("id") and _item["id"] != _demo._metadata.item_id:
        raise RuntimeError("Configured Metadata item ID does not match the Fabric item returned by the API.")
    if _item.get("type") and _item["type"] != "Lakehouse":
        raise RuntimeError("Configured Metadata item must be a Lakehouse.")
    if any(
        (
            (_demo.context.paths[key].workspace_id, _demo.context.paths[key].item_id)
            == (_demo._metadata.workspace_id, _demo._metadata.item_id)
            for key in ("Bronze", "Silver", "Gold")
        )
    ):
        raise RuntimeError("Metadata must be separate from the business stores.")
    _demo_check_processing_boundary(_demo)
    _silver = _demo.context.paths["Silver"]
    _workspace_name = _demo._demo_client.request("GET", f"/workspaces/{_silver.workspace_id}")["displayName"]
    _item_name = _demo._demo_client.request("GET", f"/workspaces/{_silver.workspace_id}/items/{_silver.item_id}")[
        "displayName"
    ]
    _demo._demo_silver_catalog = ".".join(
        ("`" + name.replace("`", "``") + "`" for name in (_workspace_name, _item_name, "demo"))
    )
    _bronze = _demo.context.paths["Bronze"]
    _bronze_workspace = _demo._demo_client.request("GET", f"/workspaces/{_bronze.workspace_id}")["displayName"]
    _bronze_item = _demo._demo_client.request("GET", f"/workspaces/{_bronze.workspace_id}/items/{_bronze.item_id}")["displayName"]
    _demo._demo_bronze_catalog = ".".join("`" + name.replace("`", "``") + "`" for name in (_bronze_workspace, _bronze_item, "demo"))
    with ExitStack() as cleanup:
        _demo_day1 = {}
        for (_store, _table), (_file, _count) in _DEMO_SOURCES.items():
            _frame = read_lakehouse_csv(_file, store="Bronze", header=True, inferSchema=True).cache()
            cleanup.callback(_frame.unpersist)
            if _frame.count() != _count:
                raise RuntimeError(f"{_file} must contain {_count} rows. Restore the fixture before resetting.")
            _demo_day1[_store, _table] = _frame
        _demo_remove_outputs(_demo, preview=True)
        # Resolve the existing Gold schema before changing metadata or business data.
        # A missing demo output needs no write and must stay missing on repeat reset.
        _demo._demo_gold_empty_output = _demo_prepare_gold_empty_output()
        _demo_clear_metadata(_demo, _demo_counts)
        if any(_demo_metadata_counts(_demo).values()):
            raise RuntimeError(
                "Metadata reset incomplete. Stop all demo writers and rerun orchestrate_demo_reset(reset=True)."
            )
        _demo_remove_outputs(_demo)
        for (_store, _table), _expected in _demo_day1.items():
            if (_store, _table) == ("Bronze", "orders"):
                continue  # Validated CSV is the source; never recreate its redundant table.
            _writer = write_warehouse_table if _store == "Gold" else write_lakehouse_table
            _reader = read_warehouse_table if _store == "Gold" else read_lakehouse_table
            _writer(_expected, table_name=_table, store=_store, schema="demo", mode="overwrite")
            _demo_assert_source(_demo, _reader(table_name=_table, store=_store, schema="demo"), _expected)
        _demo_verify_outputs(_demo)
        if any(_demo_metadata_counts(_demo).values()):
            raise RuntimeError(
                "Metadata changed during preparation. Stop demo writers and rerun orchestrate_demo_reset(reset=True)."
            )
    print("RESET COMPLETE")
