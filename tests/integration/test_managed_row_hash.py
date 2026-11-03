"""Executable canonical row hash contract on local Spark."""
# ruff: noqa: D103
from datetime import datetime
from decimal import Decimal

import pytest
from pyspark.sql import functions as F

from fabricops_kit.pipeline.shared import add_row_hash

pytestmark = pytest.mark.spark


def test_hash_canonicalizes_order_nulls_nested_types_and_generated_fields(spark_session):
    frame = spark_session.createDataFrame(
        [(1, None, {'b': 2, 'a': 1}, [1, None], Decimal('1.20'), datetime(2026, 1, 1, 0, 0, 0, 123456))],
        'id long, value string, labels map<string,int>, items array<int>, price decimal(8,2), event_time timestamp')
    original = add_row_hash(frame).first()._row_hash
    assert len(original) == 64
    assert add_row_hash(frame.select(*reversed(frame.columns))).first()._row_hash == original
    assert add_row_hash(frame.withColumn('_activity_id', F.lit('another-run'))
                        .withColumn('_row_hash', F.lit('untrusted'))).first()._row_hash == original
    assert add_row_hash(frame.withColumn('value', F.lit(''))).first()._row_hash != original
    assert add_row_hash(frame.withColumn('id', F.col('id').cast('string'))).first()._row_hash != original
    assert add_row_hash(frame.withColumn('event_time', F.col('event_time') + F.expr('INTERVAL 1 MICROSECOND'))).first()._row_hash != original
    assert add_row_hash(frame.limit(0)).count() == 0
    assert add_row_hash(frame.unionByName(frame)).select('_row_hash').distinct().count() == 1


def test_source_supplied_jobs_and_timestamps_are_hashed(spark_session):
    frame = spark_session.createDataFrame([(1, 'job-1', '2026-01-01')], 'id int, pipeline_run_id string, ingested_at_utc string')
    original = add_row_hash(frame).first()._row_hash
    for name in ('pipeline_run_id', 'ingested_at_utc'):
        assert add_row_hash(frame.withColumn(name, F.lit('changed'))).first()._row_hash != original


def test_struct_order_and_session_timezone_do_not_change_hash(spark_session):
    frame = spark_session.sql("SELECT named_struct('b', 2, 'a', 1) nested, timestamp'2026-01-01 00:00:00' ts")
    original = add_row_hash(frame).first()._row_hash
    reordered = frame.select(F.struct('nested.a', 'nested.b').alias('nested'), 'ts')
    assert add_row_hash(reordered).first()._row_hash == original
    previous = spark_session.conf.get('spark.sql.session.timeZone')
    try:
        spark_session.conf.set('spark.sql.session.timeZone', 'Asia/Singapore')
        assert add_row_hash(frame).first()._row_hash == original
    finally:
        spark_session.conf.set('spark.sql.session.timeZone', previous)


def test_existing_targets_require_valid_hashes(spark_session, monkeypatch):
    from fabricops_kit.pipeline import shared
    identity = {'store_type': 'lakehouse', 'store': 'Silver', 'table_name': 'target'}
    frame = spark_session.createDataFrame([(1,)], 'id int')
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: frame)
    with pytest.raises(ValueError, match='no _row_hash'):
        shared.validate_target_row_hash(identity, context={})
    frame = frame.withColumn('_row_hash', F.lit(None).cast('string'))
    with pytest.raises(ValueError, match='invalid historical'):
        shared.validate_target_row_hash(identity, context={})
    frame = add_row_hash(frame)
    shared.validate_target_row_hash(identity, context={})


def test_hash_v1_golden_serialization_and_final_treated_values(spark_session):
    import hashlib
    frame = spark_session.createDataFrame([(1, None)], 'x int, v string')
    expected = hashlib.sha256(b'{"version":1,"columns":[["v","string"],["x","int"]]}\n{"v":null,"x":1}').hexdigest()
    assert add_row_hash(frame).first()._row_hash == expected
    treated = add_row_hash(frame).withColumn('v', F.lit('tokenized-value'))
    actual = add_row_hash(treated).first()._row_hash
    assert actual != expected
    assert actual == add_row_hash(treated.drop('_row_hash')).first()._row_hash
