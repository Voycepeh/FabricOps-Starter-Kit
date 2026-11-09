"""Public orchestrator for the disposable FabricOps Guided Demo environment."""

from __future__ import annotations

import json
from urllib.error import HTTPError

from fabricops_kit.activated_pipeline.shared import FabricNotebookClient, snapshot_file
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
    execute_warehouse_sql,
    get_spark_session,
    resolve_configured_lakehouse_table,
    resolve_warehouse_name,
)
from fabricops_kit.pipeline.shared import resolve_physical_table_identity

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
_DEMO_NAMES = {"02A_full_refresh_demo", "02B_incremental_append_demo", "02C_scd_demo"}


class _DemoReset:
    """Private state for one demo reset invocation; never shared between calls."""

    def __init__(self, config, setup, runtime, spark):
        self._demo_config = config
        self.context = setup
        self._demo_runtime = runtime
        self.spark = spark

    def _demo_metadata_counts(self):
        """Read every installed metadata schema without modifying its records or history."""
        counts = {}
        for table, expected in metadata_table_schema_registry().items():
            schema = metadata_table_physical_schema(self._demo_config, table)
            try:
                frame = read_lakehouse_table(table, store="Metadata", schema=schema)
            except Exception as exc:
                raise RuntimeError(
                    f"Cannot read {schema}.{table}. Check the demo Metadata mapping and run metadata setup in 00B."
                ) from exc
            actual = {field.name: field.dataType.simpleString() for field in frame.schema}
            incompatible = [field.name for field in expected if actual.get(field.name) != field.dataType.simpleString()]
            if incompatible:
                raise RuntimeError(
                    f"{table} has missing columns or incompatible types: {', '.join(incompatible)}. Run the installed package metadata setup in the demo lakehouse, then restart 00C."
                )
            counts[table] = frame.count()
        return counts

    def _demo_assert_source(self, actual, expected):
        """Compare full row multisets after normalizing Warehouse connector data types."""
        from pyspark.sql import functions as F

        actual = actual.select(*[F.col(field.name).cast(field.dataType).alias(field.name) for field in expected.schema])
        if actual.exceptAll(expected).limit(1).count() or expected.exceptAll(actual).limit(1).count():
            raise RuntimeError(
                "Day 1 source verification failed: persisted content differs from the fixture. Rerun 00C."
            )

    def _demo_check_jobs(self):
        """Check current and retained promoted demo notebooks before resetting."""
        jobs = set()
        page = f"/workspaces/{self.context.workspace_id}/notebooks"
        while page:
            payload = self._demo_client.request("GET", page)
            jobs.update(
                (
                    (self.context.workspace_id, item["id"])
                    for item in payload["value"]
                    if item["displayName"] in _DEMO_NAMES
                )
            )
            page = payload.get("continuationUri")
        for row in read_lakehouse_table(
            "METADATA_PIPELINE_REGISTRY",
            store="Metadata",
            schema=metadata_table_physical_schema(self._demo_config, "METADATA_PIPELINE_REGISTRY"),
        ).collect():
            jobs.add((row["source_workspace_id"], row["source_notebook_id"]))
            jobs.add((row["execution_workspace_id"], row["governed_notebook_id"]))
        for row in (
            read_lakehouse_table(
                "METADATA_PIPELINE_RUN",
                store="Metadata",
                schema=metadata_table_physical_schema(self._demo_config, "METADATA_PIPELINE_RUN"),
            )
            .select("_workspace_id", "_notebook_id")
            .distinct()
            .collect()
        ):
            jobs.add((row["_workspace_id"], row["_notebook_id"]))
        jobs.discard((self.context.workspace_id, self._demo_runtime.get("notebook_id")))
        for workspace, notebook in jobs:
            path = f"/workspaces/{workspace}/items/{notebook}/jobs/instances"
            while path:
                try:
                    payload = self._demo_client.request("GET", path)
                except HTTPError as exc:
                    if exc.code != 404:
                        raise
                    try:
                        self._demo_client.request("GET", f"/workspaces/{workspace}/items/{notebook}")
                    except HTTPError as missing:
                        error = json.loads(missing.read()) if missing.code == 404 else {}
                        if missing.code == 404 and error.get("errorCode") == "ItemNotFound":
                            break
                        raise
                    raise RuntimeError(
                        "Cannot check demo notebook jobs. Stop executions and check Fabric permissions."
                    ) from exc
                if any(
                    (job["status"] not in {"Completed", "Failed", "Cancelled", "Deduped"} for job in payload["value"])
                ):
                    raise RuntimeError("A demo notebook job is active. Stop demo executions before reset=True.")
                path = payload.get("continuationUri")

    def _demo_check_metadata_scope(self, value):
        """Reject references outside the configured demo before clearing its dedicated metadata."""
        if isinstance(value, list):
            for item in value:
                self._demo_check_metadata_scope(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key in {"table_id", "source_table_id", "target_table_id", "incremental_target_table_id"}:
                    if item and item not in self._demo_table_ids:
                        raise RuntimeError(f"Non-demo table reference in {key}; metadata is preserved.")
                elif key == "source_table_ids" and item:
                    if not set(item).issubset(self._demo_table_ids):
                        raise RuntimeError("Non-demo source references; metadata is preserved.")
                elif key in {
                    "workspace_id",
                    "_workspace_id",
                    "execution_workspace_id",
                    "source_workspace_id",
                    "evidence_workspace_id",
                }:
                    if item and str(item).casefold() not in self._demo_workspaces:
                        raise RuntimeError("Non-demo workspace reference; metadata is preserved.")
                elif key in {
                    "operations",
                    "profiling",
                    "operations_json",
                    "package_json",
                    "contract_payload_json",
                    "destination_json",
                }:
                    self._demo_check_metadata_scope(json.loads(item) if isinstance(item, str) else item)
                elif isinstance(item, (dict, list)):
                    self._demo_check_metadata_scope(item)

    def _demo_metadata_files(self, *, delete=False):
        """Inspect or clear only the three native lifecycle artifact folders in demo Metadata."""
        folders = {"submissions": ".json", "dry_runs": ".json", "pipeline_snapshots": ".ipynb"}
        counts = {}
        for folder, suffix in folders.items():
            uri = self._metadata.root + "/Files/fabricops/engineering/" + folder
            path = self.spark._jvm.org.apache.hadoop.fs.Path(uri)
            fs = path.getFileSystem(self.spark._jsc.hadoopConfiguration())
            counts[folder] = 0
            if not fs.exists(path):
                continue
            files = fs.listFiles(path, True)
            while files.hasNext():
                file = files.next().getPath()
                if not str(file.getName()).endswith(suffix):
                    raise RuntimeError(
                        f"Unexpected content in {uri}; metadata is preserved. Inspect it before resetting."
                    )
                payload = json.loads(snapshot_file(str(file), spark_session=self.spark))
                self._demo_check_metadata_scope(payload)
                counts[folder] += 1
            if delete and (not fs.delete(path, True) or fs.exists(path)):
                raise RuntimeError(
                    f"Could not clear {uri}. Check permissions and rerun orchestrate_demo_reset(reset=True)."
                )
        return counts

    def _demo_remove_outputs(self, *, preview=False):
        """Remove exact configured output objects and their physical publication markers."""
        import notebookutils

        for store, table in _DEMO_OUTPUTS:
            if store == "Gold":
                if preview:
                    continue
                gold = self.context.paths[store]
                execute_warehouse_sql(
                    self.spark,
                    gold,
                    "IF OBJECT_ID(N'demo.customer_summary', N'U') IS NOT NULL DROP TABLE [demo].[customer_summary]; SELECT 1 AS demo_reset_dropped;",
                    database_name=resolve_warehouse_name(gold, store),
                )
            else:
                _, _, _, path = resolve_configured_lakehouse_table(store, table, "demo")
                qualified = f"{self._demo_silver_catalog}.`{table}`"
                if self.spark.catalog.tableExists(qualified):
                    location_rows = (
                        self.spark.sql(f"DESCRIBE TABLE EXTENDED {qualified}").where("col_name = 'Location'").collect()
                    )
                    if len(location_rows) != 1 or location_rows[0]["data_type"].rstrip("/") != path.rstrip("/"):
                        raise RuntimeError(f"Catalog location mismatch for {store}.demo.{table}; reset blocked.")
                    if not preview:
                        self.spark.sql(f"DROP TABLE {qualified}")
                if not preview and notebookutils.fs.exists(path) and (not notebookutils.fs.rm(path, True)):
                    raise RuntimeError(f"Could not remove {store}.demo.{table}; check permissions and retry 00C.")
            if not preview:
                print(f"Removed output (missing is OK): {store}.demo.{table}")

    def _demo_verify_outputs(self):
        """Fail if any of the six physical outputs still exists."""
        import notebookutils

        for store, table in _DEMO_OUTPUTS:
            if store == "Gold":
                exists = (
                    read_warehouse_query(
                        "SELECT COUNT(*) AS n FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name='demo' AND t.name='customer_summary'",
                        store="Gold",
                    ).first()["n"]
                    != 0
                )
            else:
                _, _, _, path = resolve_configured_lakehouse_table(store, table, "demo")
                exists = notebookutils.fs.exists(path) or self.spark.catalog.tableExists(
                    f"{self._demo_silver_catalog}.`{table}`"
                )
            if exists:
                raise RuntimeError(f"Reset incomplete: {store}.demo.{table} remains. Check permissions and rerun 00C.")

    def _demo_clear_metadata(self, counts, order):
        """Clear only the validated demo inventory, retaining physical table definitions."""
        from delta.tables import DeltaTable

        for _table in order:
            _, _, _, _path = resolve_configured_lakehouse_table(
                "Metadata", _table, metadata_table_physical_schema(self._demo_config, _table)
            )
            _removed = 0
            if counts[_table]:
                _delta = DeltaTable.forPath(self.spark, _path)
                _delta.delete()
                _removed = int(_delta.history(1).first()["operationMetrics"]["numDeletedRows"])
            print(f"{_table}: removed {_removed}")


def orchestrate_demo_reset(*, reset: bool = False) -> None:
    """Preview or reset the dedicated FabricOps Guided Demo to Day 1.

    Call after ``setup_notebook()`` with the package being validated installed.
    The configured logical ``Metadata`` store must select a manually created,
    schema-enabled Lakehouse named ``demo_metadata``, reserved exclusively for
    this walkthrough. Stop all demo executions and schedules before resetting.

    Parameters
    ----------
    reset : bool, default=False
        False prints configured store identities, metadata row counts and the
        eleven business tables in scope without writing. True opts into the
        destructive reset after all preflight checks pass. Only booleans are
        accepted; strings and integers are rejected.

    Returns
    -------
    None
        Prints a preview or verified reset summary, including actual removed
        metadata counts. ``RESET COMPLETE`` is printed only after verification.

    Raises
    ------
    ValueError
        If reset is not a boolean.
    RuntimeError
        If notebook setup is not ready, required stores or metadata schemas
        are invalid, non-demo references or active jobs are found, fixtures
        are unavailable, or reset verification fails. Fabric/Spark permission,
        transport and storage failures propagate; correct the cause and rerun.

    Notes
    -----
    True clears all current canonical metadata rows in the dedicated item,
    including frozen Contracts, activations, approvals, promotion history,
    Runs and Processing State. Saved submissions, Dry Run evidence and notebook
    snapshots in its three native lifecycle folders are removed too. Table
    definitions remain; no metadata migration is performed.

    Five Day 1 sources are overwritten and six outputs removed in the reserved
    ``demo`` schemas of the configured Bronze/Silver/Gold stores. Other business
    tables and source files are preserved. Exact demo table/workspace references,
    relevant jobs, artifact contents, fixture counts and catalog locations are
    checked before deletion. A dedicated name alone cannot prove ownership;
    never share this Metadata item or these eleven tables with other projects.

    Missing outputs and repeated resets are supported. A failure may leave a
    partial reset: this operation is not atomic across tables/stores. Stop all
    writers, correct the reported cause and rerun. Deployed notebooks, schedules
    and apps are not removed. Live Fabric acceptance is still required.

    Examples
    --------
    >>> from fabricops_kit import setup_notebook, orchestrate_demo_reset
    >>> context = setup_notebook()
    >>> RESET_DEMO = False  # Set True only to discard the dedicated demo state.
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
    for key, kind in {'Bronze': 'lakehouse', 'Silver': 'lakehouse', 'Gold': 'warehouse'}.items():
        store = setup.paths[key]
        if store.kind != kind or (kind == 'lakehouse' and not store.schema_enabled):
            raise RuntimeError(f'Demo requires {key} to be a {kind} with the demo schema. Check 00_env_config.')
    _demo = _DemoReset(config, setup, runtime, get_spark_session())
    _demo._metadata = _demo.context.paths["Metadata"]
    if _demo._metadata.kind != "lakehouse" or not _demo._metadata.schema_enabled:
        raise RuntimeError("Metadata must be a schema-enabled Lakehouse.")
    for _key in ("Metadata", "Bronze", "Silver", "Gold"):
        _store = _demo.context.paths[_key]
        print(f"{_key}: {_store.name} | workspace {_store.workspace_id} | item {_store.item_id}")
    _demo_counts = _demo._demo_metadata_counts()
    for _table, _count in _demo_counts.items():
        print(f"{_table}: {_count} rows")
    for _store, _table in _DEMO_SOURCES:
        print(f"Restore Day 1: {_store}.demo.{_table}")
    for _store, _table in _DEMO_OUTPUTS:
        print(f"Remove output: {_store}.demo.{_table}")
    if not reset:
        print("Preview only. Stop demo executions and set reset=True to reset.")
        return
    _demo._demo_client = FabricNotebookClient()
    _item = _demo._demo_client.request(
        "GET", f"/workspaces/{_demo._metadata.workspace_id}/items/{_demo._metadata.item_id}"
    )
    if _item["displayName"] != "demo_metadata" or _demo._metadata.name != "demo_metadata":
        raise RuntimeError(
            "Reset requires the manually created dedicated demo_metadata item selected in 00_env_config."
        )
    if any(
        (
            (_demo.context.paths[key].workspace_id, _demo.context.paths[key].item_id)
            == (_demo._metadata.workspace_id, _demo._metadata.item_id)
            for key in ("Bronze", "Silver", "Gold")
        )
    ):
        raise RuntimeError("Metadata must be separate from the business stores.")
    _demo._demo_table_ids = {
        resolve_physical_table_identity(_demo._demo_config, workspace, store=store, schema="demo", table_name=table)[
            "table_id"
        ]
        for workspace, stores in _demo._demo_config.path_config.paths.items()
        for store, table in [*_DEMO_SOURCES, *_DEMO_OUTPUTS]
        if store in stores
    }
    _demo._demo_workspaces = {workspace.casefold() for workspace in _demo._demo_config.path_config.paths}
    _demo._demo_workspaces.update((store.workspace_id.casefold() for store in _demo.context.paths.values()))
    _demo_order = (
        "METADATA_GUARDRAIL_RESULTS",
        "METADATA_PROCESSING_STATE",
        "METADATA_DATA_LINEAGE",
        "METADATA_DATA_ACCESS",
        "METADATA_PIPELINE_RUN",
        "METADATA_PIPELINE_REGISTRY",
        "METADATA_PIPELINE_ACTIVATION",
        "METADATA_DATA_CONTRACT_ACTIVATION",
        "METADATA_DATA_PROFILED_FREQUENCY",
        "METADATA_DATA_PROFILED",
        "METADATA_DATA_CONTRACT",
        "METADATA_DATA_CATALOGUE",
        "METADATA_DATA_AGREEMENT",
        "METADATA_DATA_STEWARD",
    )
    if set(_demo_counts) != set(_demo_order):
        raise RuntimeError("Metadata inventory changed. Review reset dependencies before deleting records.")
    for _table in _demo_counts:
        for _row in read_lakehouse_table(
            _table, store="Metadata", schema=metadata_table_physical_schema(_demo._demo_config, _table)
        ).toLocalIterator():
            _demo._demo_check_metadata_scope(_row.asDict(recursive=True))
    _demo_file_counts = _demo._demo_metadata_files()
    for _folder, _count in _demo_file_counts.items():
        print(f"Metadata Files/{_folder}: {_count} artifacts")
    _demo._demo_check_jobs()
    _silver = _demo.context.paths["Silver"]
    _workspace_name = _demo._demo_client.request("GET", f"/workspaces/{_silver.workspace_id}")["displayName"]
    _item_name = _demo._demo_client.request("GET", f"/workspaces/{_silver.workspace_id}/items/{_silver.item_id}")[
        "displayName"
    ]
    _demo._demo_silver_catalog = ".".join(
        ("`" + name.replace("`", "``") + "`" for name in (_workspace_name, _item_name, "demo"))
    )
    _demo_day1 = {}
    for (_store, _table), (_file, _count) in _DEMO_SOURCES.items():
        _frame = read_lakehouse_csv(_file, store="Bronze", header=True, inferSchema=True).cache()
        if _frame.count() != _count:
            raise RuntimeError(f"{_file} must contain {_count} rows. Restore the fixture before resetting.")
        _demo_day1[_store, _table] = _frame
    _demo._demo_remove_outputs(preview=True)
    _demo._demo_clear_metadata(_demo_counts, _demo_order)
    if any(_demo._demo_metadata_counts().values()):
        raise RuntimeError(
            "Metadata reset incomplete. Stop all demo writers and rerun orchestrate_demo_reset(reset=True)."
        )
    _demo_removed_files = _demo._demo_metadata_files(delete=True)
    for _folder, _count in _demo_removed_files.items():
        print(f"Metadata Files/{_folder}: removed {_count}")
    _demo._demo_remove_outputs()
    for (_store, _table), _expected in _demo_day1.items():
        _writer = write_warehouse_table if _store == "Gold" else write_lakehouse_table
        _reader = read_warehouse_table if _store == "Gold" else read_lakehouse_table
        _writer(_expected, table_name=_table, store=_store, schema="demo", mode="overwrite")
        _demo._demo_assert_source(_reader(table_name=_table, store=_store, schema="demo"), _expected)
    _demo._demo_verify_outputs()
    if any(_demo._demo_metadata_counts().values()):
        raise RuntimeError(
            "Metadata changed during preparation. Stop demo writers and rerun orchestrate_demo_reset(reset=True)."
        )
    if any(_demo._demo_metadata_files().values()):
        raise RuntimeError(
            "Lifecycle artifacts remain. Stop demo writers and rerun orchestrate_demo_reset(reset=True)."
        )
    for _frame in _demo_day1.values():
        _frame.unpersist()
    print("RESET COMPLETE")
