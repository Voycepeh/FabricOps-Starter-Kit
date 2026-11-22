"""Upgrade the released v0.5.0 participation layout without losing Delta history."""
from datetime import datetime
from importlib import import_module

import pytest

from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry

pytestmark = pytest.mark.spark


def test_lineage_additive_upgrade_preserves_legacy_rows_and_extensions(spark_session, monkeypatch, tmp_path):
    """Bootstrap adds nullable fact fields, never reclassifying legacy activity as a dependency."""
    pytest.importorskip('delta.tables')
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    from pyspark.sql.types import StructType, StructField, StringType, TimestampType
    setup = import_module('fabricops_kit.config.setup_metadata_tables')
    path = str(tmp_path / 'lineage')
    # Frozen v0.5.0 schema, plus a consumer-owned extension.
    fields = ['lineage_id', 'table_id', 'table_name', 'workspace_id', 'pipeline_role', 'consumer_extension']
    legacy = StructType([StructField(name, StringType(), True) for name in fields] +
        [StructField(name, TimestampType() if kind == 'timestamp' else StringType(), False)
         for name, kind, _ in AUDIT_SCHEMA_FIELDS])
    old = {name: ' keep exact bytes \n ' for name in fields}
    old.update({name: datetime(2020, 1, 2, 3, 4, 5, 123456) if kind == 'timestamp' else 'legacy'
                for name, kind, _ in AUDIT_SCHEMA_FIELDS})
    spark_session.createDataFrame([old], legacy).write.format('delta').save(path)
    writes = []
    def write(frame, table, **kwargs):
        writes.append(table)
        frame.write.format('delta').mode('append').option('mergeSchema', 'true').save(path)
    monkeypatch.setattr(setup, 'write_lakehouse_table', write)
    expected = metadata_table_schema_registry()['METADATA_DATA_LINEAGE']
    for _ in range(2):
        current = spark_session.read.format('delta').load(path)
        missing = setup._validate_existing_metadata_schema('METADATA_DATA_LINEAGE', current.schema, expected, allow_missing=True)
        if missing:
            setup._add_missing_metadata_columns(spark=spark_session, table_name='METADATA_DATA_LINEAGE',
                metadata_schema='engineering', expected_schema=expected, missing_columns=missing, context={})
    upgraded = spark_session.read.format('delta').load(path).collect()
    assert len(writes) == 1 and len(upgraded) == 1
    retained = upgraded[0].asDict()
    assert {name: retained[name] for name in old} == old
    assert retained['lineage_version'] is retained['run_id'] is retained['record_type'] is None
