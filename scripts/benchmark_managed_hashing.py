"""Reproduce local Spark costs; these measurements are not Fabric capacity benchmarks."""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pyspark.sql import SparkSession, functions as F

from fabricops_kit.pipeline import shared


def measure(results, name, operation):
    """Record one materialized Spark operation in seconds."""
    started = time.perf_counter()
    value = operation()
    results[name] = round(time.perf_counter() - started, 4)
    return value


def benchmark(spark, size):
    """Separate hash, distributed comparison, full observation and receipt identity costs."""
    result = {'rows': size, 'seconds': {}}
    seconds = result['seconds']
    base = spark.range(size).select('id', F.concat(F.lit('item-'), F.col('id')).alias('value'),
        F.when(F.col('id') % 9 != 0, F.lit('present')).alias('nullable'),
        (F.col('id') / 100).cast('decimal(18,2)').alias('amount'),
        F.expr("timestamp'2026-01-01 00:00:00' + id * INTERVAL 1 MICROSECOND").alias('source_timestamp'),
        F.create_map(F.lit('b'), F.col('id'), F.lit('a'), F.lit(1)).alias('attributes')).cache()
    base.count()
    hashed = shared.add_row_hash(base).cache()
    try:
        digest_length = measure(seconds, 'hash_calculation_and_cache',
            lambda: hashed.agg(F.sum(F.length('_row_hash')).alias('n')).first().n)
        assert digest_length == size * 64
        seen = hashed.where(F.col('id') < size // 2).select('_row_hash')
        unseen = measure(seconds, 'distributed_target_hash_comparison',
            lambda: hashed.dropDuplicates(['_row_hash']).join(seen, '_row_hash', 'left_anti').count())
        assert unseen == size - size // 2
        measure(seconds, 'cached_publication_multiset_aggregate', lambda: shared.row_hash_totals(hashed))
        hashed.unpersist()
        plan = SimpleNamespace(plan_id='benchmark', pipeline_id='benchmark-pipeline', permits_persistence=True,
            evidence={'source_observation_policy': {'manual': True, 'days': None}})
        context = dict(config=object(), scope_workspace_id='benchmark', execution_plan=plan)
        identity = dict(table_id='source', table_name='source', store='Bronze', store_type='lakehouse')
        with patch.object(shared, 'read_lakehouse_table', return_value=[]), \
             patch.object(shared, 'metadata_table_physical_schema', return_value=None), \
             patch.object(shared, '_merge_source_observation_records'), \
             patch.object(shared, '_find_applied_publication', return_value=None), \
             patch.object(shared, 'build_pipeline_audit_fields', return_value={'_committed_at': datetime.now(UTC)}):
            observed = measure(seconds, 'full_source_observation_cached_read',
                lambda: shared.observe_full_source(identity, dataframe=base, context=context))
            assert observed['row_count'] == size
            def publication():
                with shared.PublicationBatch(base, identity={'table_id': 'target'}, processing={'load_strategy': 'append_all'},
                    source_table_ids=[], audit={'_activity_id': 'benchmark'}, context=context) as batch:
                    assert batch.input_rows == size
            measure(seconds, 'publication_hash_aggregate_and_mocked_receipt_lookup', publication)
        hashed.persist()
        hashed.count()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            measure(seconds, 'parquet_write_without_hash', lambda: base.write.parquet(str(root / 'plain')))
            measure(seconds, 'parquet_write_with_hash', lambda: hashed.write.parquet(str(root / 'hashed')))
            result['parquet_bytes'] = {kind: sum(path.stat().st_size for path in (root / kind).glob('*.parquet'))
                                       for kind in ('plain', 'hashed')}
        result['unseen_rows'] = unseen
        return result
    finally:
        hashed.unpersist()
        base.unpersist()


def main():
    """Run bounded local measurements and write machine-readable results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', default='100000,1000000')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    spark = (SparkSession.builder.master('local[2]').appName('managed-hashing-benchmark')
             .config('spark.driver.host', '127.0.0.1').config('spark.driver.bindAddress', '127.0.0.1')
             .config('spark.ui.enabled', 'false').config('spark.sql.shuffle.partitions', '4').getOrCreate())
    spark.sparkContext.setLogLevel('ERROR')
    try:
        results = {'runtime': 'local Spark ' + spark.version, 'workers': 2,
                   'limitations': 'Single measurements; cached synthetic source, Parquet writes and mocked metadata transport. No Fabric capacity, Warehouse service or metadata transaction latency claims.',
                   'measurements': [benchmark(spark, int(size)) for size in args.rows.split(',')]}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(results, indent=2))
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
