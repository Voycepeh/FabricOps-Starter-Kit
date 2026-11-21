"""Diagram primary keys are enforced on real Delta, including competing inserts."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, local

import pytest

from fabricops_kit.config.metadata_schemas import METADATA_PRIMARY_KEYS
from fabricops_kit.io.shared import validate_metadata_primary_key, write_metadata_frame

pytestmark = pytest.mark.spark


@pytest.fixture
def keyed_delta(spark_session, tmp_path):
    """Create a nullable physical layout so runtime checks must enforce the key."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    def create(table):
        path = str(tmp_path / table)
        schema = ", ".join(f"{name} STRING" for name in (*METADATA_PRIMARY_KEYS[table], "payload"))
        spark_session.createDataFrame([], schema).write.format("delta").option("delta.isolationLevel", "Serializable").save(path)
        def frame(key="one", payload="original"):
            return spark_session.createDataFrame([tuple([key] * len(METADATA_PRIMARY_KEYS[table]) + [payload])], schema)
        return path, frame
    return spark_session, create


@pytest.mark.parametrize("table", METADATA_PRIMARY_KEYS)
def test_each_diagram_key_rejects_duplicate_inserts(keyed_delta, table):
    """Every declared key blocks duplicate rows while permitting a distinct identity."""
    spark, create = keyed_delta
    path, frame = create(table)
    write_metadata_frame(frame(), path, table)
    with pytest.raises(ValueError, match="already exists"):
        write_metadata_frame(frame(payload="conflict"), path, table)
    write_metadata_frame(frame("two"), path, table)
    assert spark.read.format("delta").load(path).count() == 2


def test_duplicate_and_missing_keys_preserve_existing_rows(keyed_delta):
    """Nulls, blanks and duplicates within a batch fail before publication."""
    spark, create = keyed_delta
    table = "METADATA_DATA_CONTRACT"
    path, frame = create(table)
    write_metadata_frame(frame(), path, table)
    for invalid in (frame(None), frame(" "), frame("two").unionByName(frame("two"))):
        with pytest.raises(ValueError, match="primary key"):
            write_metadata_frame(invalid, path, table)
    assert spark.read.format("delta").load(path).count() == 1
    # Versions are distinct row identities within the same Contract lifecycle.
    write_metadata_frame(spark.createDataFrame([("one", "two", "next")], frame().schema), path, table)
    assert spark.read.format("delta").load(path).count() == 2


@pytest.mark.parametrize("same_key", [True, False])
def test_competing_appends_recheck_pinned_keys(keyed_delta, monkeypatch, same_key):
    """Force both writers to read the empty version before either commits."""
    import fabricops_kit.io.shared as io

    spark, create = keyed_delta
    table = "METADATA_DATA_CONTRACT"
    path, frame = create(table)
    barrier, state = Barrier(2), local()
    def validate(table, candidate):
        state.calls = getattr(state, "calls", 0) + 1
        if state.calls == 2:
            barrier.wait(timeout=60)
        validate_metadata_primary_key(table, candidate)
    monkeypatch.setattr(io, "validate_metadata_primary_key", validate)
    def insert(index):
        try:
            write_metadata_frame(frame("same" if same_key else str(index), str(index)), path, table)
            return "committed"
        except ValueError as exc:
            assert "already exists" in str(exc)
            return "duplicate"
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(insert, range(2)))
    assert sorted(outcomes) == (["committed", "duplicate"] if same_key else ["committed", "committed"])
    stored = spark.read.format("delta").load(path)
    assert stored.count() == (1 if same_key else 2)
    validate_metadata_primary_key(table, stored)


def test_steward_update_and_transaction_replay_remain_one_row(keyed_delta):
    """Steward edits replace a row; replay identities cannot introduce a duplicate."""
    spark, create = keyed_delta
    table = "METADATA_DATA_STEWARD"
    path, frame = create(table)
    write_metadata_frame(frame(), path, table)
    write_metadata_frame(frame(payload="edited"), path, table, mode="upsert")
    assert [row.payload for row in spark.read.format("delta").load(path).collect()] == ["edited"]
    options = {"txnAppId": "test-observation", "txnVersion": 1}
    write_metadata_frame(frame("two"), path, table, options=options)
    write_metadata_frame(frame("two"), path, table, options=options)
    assert spark.read.format("delta").load(path).count() == 2


def test_corrupt_retained_keys_are_not_silently_repaired(keyed_delta):
    """An external duplicate blocks toolkit writes without losing retained content."""
    spark, create = keyed_delta
    table = "METADATA_DATA_STEWARD"
    path, frame = create(table)
    frame().unionByName(frame()).write.format("delta").mode("append").save(path)
    with pytest.raises(ValueError, match="primary key"):
        write_metadata_frame(frame("new"), path, table)
    assert spark.read.format("delta").load(path).count() == 2


def test_setup_enables_keys_idempotently_and_blocks_blank_external_keys(keyed_delta, monkeypatch):
    """Setup preserves valid rows, adds required-key constraints and can be repeated."""
    import importlib
    from delta.tables import DeltaTable

    setup = importlib.import_module("fabricops_kit.config.setup_metadata_tables")
    spark, create = keyed_delta
    table = "METADATA_DATA_CONTRACT"
    path, frame = create(table)
    frame().write.format("delta").mode("append").save(path)
    spark.sql(f"ALTER TABLE delta.`{path}` UNSET TBLPROPERTIES ('delta.isolationLevel')")
    monkeypatch.setattr(setup, "resolve_configured_lakehouse_table", lambda *a, **kw: (None, table, "governance", path))
    for _ in range(2):
        setup._enforce_metadata_primary_key(spark=spark, table=spark.read.format("delta").load(path),
            table_name=table, metadata_schema="governance", context={})
    properties = DeltaTable.forPath(spark, path).detail().select("properties").first()["properties"]
    assert properties["delta.isolationLevel"] == "Serializable"
    assert "delta.constraints.fabricops_primary_key_required" in properties
    with pytest.raises(Exception, match="(?i)constraint|invariant"):
        frame(" ").write.format("delta").mode("append").save(path)
    assert spark.read.format("delta").load(path).count() == 1


def test_native_catalogue_merge_preserves_composite_key_under_contention(keyed_delta, monkeypatch, tmp_path):
    """Two native MERGEs of the same new Catalogue key leave one physical row."""
    from datetime import datetime
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
    from fabricops_kit.pipeline import shared

    spark, _ = keyed_delta
    table = "METADATA_DATA_CATALOGUE"
    path = str(tmp_path / "catalogue")
    spark.createDataFrame([], metadata_table_schema_registry()[table]).write.format("delta").option("delta.isolationLevel", "Serializable").save(path)
    monkeypatch.setattr(shared, "resolve_configured_lakehouse_table", lambda *a, **kw: (None, table, "engineering", path))
    barrier = Barrier(2)
    audit = {name: datetime(2026, 1, 1) if name == "_committed_at" else "test" for name, *_ in AUDIT_SCHEMA_FIELDS}
    def insert(index):
        barrier.wait(timeout=60)
        shared.merge_catalogue_asset({**audit, "asset_workspace_id": "physical", "table_id": "orders", "asset_type": "TABLE",
            "table_name": "orders", "item_id": "item", "is_active": True}, context={"config": {}}, spark_session=spark)
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(insert, range(2)))
    stored = spark.read.format("delta").load(path)
    assert stored.count() == 1
    validate_metadata_primary_key(table, stored)


def test_append_and_steward_edits_preserve_extension_columns(keyed_delta):
    """Canonical frames can omit a nullable extension without erasing an edited value."""
    from pyspark.sql import functions as F

    spark, create = keyed_delta
    table = "METADATA_DATA_STEWARD"
    path, frame = create(table)
    extended = frame().withColumn("extension", F.lit("retained"))
    extended.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
    write_metadata_frame(frame(payload="edited"), path, table, mode="upsert")
    write_metadata_frame(frame("new"), path, table)
    stored = {row.steward_id: row.asDict() for row in spark.read.format("delta").load(path).collect()}
    assert stored["one"]["extension"] == "retained"
    assert stored["one"]["payload"] == "edited"
    assert stored["new"]["extension"] is None


def test_setup_rejects_duplicates_without_mutating_retained_table(keyed_delta, monkeypatch):
    """A setup failure leaves even the Delta history unchanged for a corrupt key set."""
    import importlib
    from delta.tables import DeltaTable

    setup = importlib.import_module("fabricops_kit.config.setup_metadata_tables")
    spark, create = keyed_delta
    table = "METADATA_DATA_CONTRACT"
    path, frame = create(table)
    frame().unionByName(frame()).write.format("delta").mode("append").save(path)
    before = DeltaTable.forPath(spark, path).history(1).first().version
    monkeypatch.setattr(setup, "resolve_configured_lakehouse_table", lambda *a, **kw: (None, table, "governance", path))
    with pytest.raises(ValueError, match="primary key"):
        setup._enforce_metadata_primary_key(spark=spark, table=spark.read.format("delta").load(path),
            table_name=table, metadata_schema="governance", context={})
    assert DeltaTable.forPath(spark, path).history(1).first().version == before
    assert spark.read.format("delta").load(path).count() == 2


def test_competing_creation_never_falls_back_to_blind_append(keyed_delta, monkeypatch, tmp_path):
    """Both writers see no table; the loser cannot append after the winner creates it."""
    from delta.tables import DeltaTable

    spark, create = keyed_delta
    table = "METADATA_DATA_CONTRACT"
    _, frame = create(table)
    path = str(tmp_path / "new-contracts")
    ready = Barrier(2)
    exists = DeltaTable.isDeltaTable
    def missing(spark, location):
        present = exists(spark, location)
        ready.wait(timeout=60)
        assert not present
        return False
    monkeypatch.setattr(DeltaTable, "isDeltaTable", missing)
    def insert(index):
        try:
            write_metadata_frame(frame("same", str(index)), path, table)
            return "committed"
        except Exception as exc:
            # Native Delta create conflicts are allowed; a second row is not.
            assert "already exists" in str(exc).lower() or "concurrent" in str(exc).lower()
            return "conflict"
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(insert, range(2)))
    assert sorted(outcomes) == ["committed", "conflict"]
    assert spark.read.format("delta").load(path).count() == 1
