"""Real Catalyst column tracing with independent expected dependencies."""
import json
from types import SimpleNamespace

# ruff: noqa: F811

import pytest

from fabricops_kit.pipeline import shared as lineage
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


@pytest.fixture
def tracked(spark_session):
    """Create a real tracker and realistic Run operation membership without Fabric IO."""
    plan = SimpleNamespace(lineage={}, runtime_context={'_pipeline_bindings': {}},
        participants_json='{}', evidence={'operations': {}})
    def read(frame, table_id, *, query=False, kind='lakehouse'):
        plan.runtime_context['_pipeline_bindings'][table_id] = {'asset_workspace_id': 'physical', 'kind': kind}
        lineage.register_read_lineage(plan, {'table_id': table_id, 'asset_type': 'TABLE', 'is_query': query, 'dataframe': frame})
        return frame
    def write(frame, table_id='output', mode='overwrite'):
        identities = json.loads(plan.participants_json)
        identities[table_id] = {'store': 'Gold', 'table_name': table_id, 'logical_id': table_id}
        plan.participants_json = json.dumps(identities)
        key = 'target:' + table_id
        plan.evidence['operations'][key] = {}
        fragment = lineage.capture_write_lineage(frame, context={'execution_plan': plan}, table_id=table_id, write_mode=mode)
        return plan.evidence['operations'][key]['lineage'], fragment
    return SimpleNamespace(spark=spark_session, plan=plan, read=read, write=write)


def roots(graph, output_name, role='VALUE'):
    """Inspect persisted root links rather than reconstructing the detector algorithm."""
    nodes = {node['node_id']: node for node in graph['nodes']}
    output = next(row for row in graph['outputs'] if row['column_name'] == output_name)
    return {(nodes[ref['node_id']]['table_id'], nodes[ref['node_id']].get('name'))
            for ref in output['sources'] if nodes[ref['node_id']]['node_type'] == 'SOURCE_COLUMN'
            and (role is None or role in ref['dependency_types'])}


def test_multi_read_multi_write_joins_filters_and_aggregation(tracked):
    """Unused Reads and discarded columns never become value dependencies."""
    from pyspark.sql import functions as F
    t = tracked
    orders = t.read(t.spark.createDataFrame([(1, 10, 2, 'active')], 'customer_id long, amount long, discount long, status string'), 'orders')
    customers = t.read(t.spark.createDataFrame([(1, 'north')], 'customer_id long, region string'), 'customers')
    t.read(t.spark.createDataFrame([(2.0,)], 'rate double'), 'unused_rates')
    def enrich(left, right):
        return left.alias('o').join(right.alias('c'), 'customer_id').filter(F.col('status') == 'active').withColumn('net', F.col('amount') - F.col('discount'))
    enriched = enrich(orders, customers)
    detail, _ = t.write(enriched, 'detail')
    summary, _ = t.write(enriched.groupBy('region').agg(F.sum('net').alias('revenue')), 'summary')
    assert detail['status'] == summary['status'] == 'complete', summary
    assert roots(detail, 'net') == {('orders', 'amount'), ('orders', 'discount')}
    assert roots(summary, 'revenue') == {('orders', 'amount'), ('orders', 'discount')}
    assert roots(summary, 'revenue', 'GROUP') >= {('customers', 'region')}
    assert roots(summary, 'revenue', 'JOIN') >= {('orders', 'customer_id'), ('customers', 'customer_id')}
    assert roots(summary, 'revenue', 'FILTER') >= {('orders', 'status')}
    assert not any(node.get('table_id') == 'unused_rates' for graph in (detail, summary) for node in graph['nodes'])
    assert {'Subtract', 'Sum', 'Join', 'Filter', 'Aggregate'} <= {node['operation'] for node in summary['nodes']}
    assert {'o', 'c'} <= {node.get('name') for node in summary['nodes']}


def test_union_by_name_self_join_and_duplicate_names(tracked):
    """Resolve union positions and self-join ExprIds independently of column names."""
    from pyspark.sql import functions as F
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, value long'), 'a')
    b = t.read(t.spark.createDataFrame([(3, 4)], 'value long, id long'), 'b')
    graph, _ = t.write(a.unionByName(b).select(F.col('value').alias('result')))
    assert graph['status'] == 'complete'
    assert roots(graph, 'result') == {('a', 'value'), ('b', 'value')}
    joined = a.alias('left').join(a.alias('right'), F.col('left.id') == F.col('right.id')).select(
        F.col('left.value').alias('first'), F.col('right.value').alias('second'))
    graph, _ = t.write(joined)
    assert graph['status'] == 'complete', graph
    assert roots(graph, 'first') == roots(graph, 'second') == {('a', 'value')}


def test_windows_case_cast_and_literals_are_redacted(tracked):
    """Keep window influences separate and never store expression literals or row data."""
    from pyspark.sql import functions as F, Window
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2, 3)], 'group_id long, sequence long, amount long'), 'a')
    result = a.withColumn('running', F.sum('amount').over(Window.partitionBy('group_id').orderBy('sequence'))).select(
        'running', F.when(F.col('amount') > 12, F.col('amount').cast('double')).otherwise(99).alias('conditional'),
        F.lit('literal-secret-value').alias('constant'))
    graph, _ = t.write(result)
    assert graph['status'] == 'complete', graph
    assert roots(graph, 'running') == {('a', 'amount')}
    assert roots(graph, 'running', 'GROUP') >= {('a', 'group_id')}
    assert roots(graph, 'running', 'ORDER') >= {('a', 'sequence')}
    assert roots(graph, 'constant') == set()
    assert 'literal-secret-value' not in json.dumps(graph)
    assert '12' not in {node.get('name') for node in graph['nodes']}


def test_cache_preserves_lineage_and_user_checkpoint_breaks_it(tracked):
    """A checkpoint cannot inherit attribution merely because column names match."""
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, value long'), 'a')
    a.cache()
    try:
        graph, _ = t.write(a.select('value'))
        assert graph['status'] == 'complete'
        snapshot = a.localCheckpoint(eager=True)
        try:
            broken, _ = t.write(snapshot.select('value'))
            assert broken['status'] == 'unknown'
            assert roots(broken, 'value') == set()
            assert broken['outputs'][0]['gaps'] == ['unregistered_or_severed_read']
        finally:
            snapshot.unpersist()
    finally:
        a.unpersist()


def test_framework_snapshot_bridge_retains_intermediate_transformations(tracked):
    """Only a framework-owned checkpoint can preserve an already captured graph."""
    from pyspark.sql import functions as F
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, amount long'), 'a')
    transformed = a.withColumn('doubled', F.col('amount') * 2)
    first, fragment = t.write(transformed, 'first')
    snapshot = transformed.localCheckpoint(eager=True)
    try:
        lineage.bridge_write_snapshot(snapshot, fragment, context={'execution_plan': t.plan})
        second, _ = t.write(snapshot.select((F.col('doubled') + 1).alias('final')), 'second')
        assert first['status'] == second['status'] == 'complete', second
        assert roots(second, 'final') == {('a', 'amount')}
        assert {'Multiply', 'Add'} <= {node['operation'] for node in second['nodes']}
    finally:
        snapshot.unpersist()


def test_opaque_udf_and_external_dataframe_have_explicit_gaps(tracked):
    """Trace UDF arguments without claiming its Python implementation is understood."""
    from pyspark.sql import functions as F
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, amount long'), 'a')
    @F.udf('long')
    def opaque(value):
        return value * 2
    graph, _ = t.write(a.select(opaque('amount').alias('result')))
    assert graph['status'] == 'partial'
    assert roots(graph, 'result') == {('a', 'amount')}
    assert graph['outputs'][0]['gaps'] == ['opaque_udf']
    # This is also the Spark-side boundary created after toPandas()/createDataFrame().
    rebuilt = t.spark.createDataFrame([(1, 2)], a.schema)
    graph, _ = t.write(rebuilt.select('amount'))
    assert graph['status'] == 'unknown' and roots(graph, 'amount') == set()


def test_query_boundaries_and_constant_generated_output(tracked):
    """Warehouse pushdown aliases cannot be assigned fabricated source column IDs."""
    from pyspark.sql import functions as F
    t = tracked
    query = t.read(t.spark.createDataFrame([(10,)], 'total long'), 'warehouse', query=True, kind='warehouse')
    graph, _ = t.write(query)
    assert graph['status'] == 'unknown' and graph['outputs'][0]['gaps'] == ['opaque_query']
    graph, _ = t.write(t.spark.range(1).select(F.lit(7).alias('constant')))
    assert graph['status'] == 'complete' and graph['outputs'][0]['sources'] == []


def test_detector_performs_no_business_row_actions(tracked, monkeypatch):
    """Metadata inspection must never count/collect a business DataFrame."""
    t = tracked
    a = t.read(t.spark.createDataFrame([(1,)], 'id long'), 'a')
    def forbidden(*args, **kwargs):
        raise AssertionError('Lineage must not evaluate business rows')
    monkeypatch.setattr(type(a), 'collect', forbidden)
    monkeypatch.setattr(type(a), 'count', forbidden)
    graph, _ = t.write(a)
    assert graph['status'] == 'complete'


def test_run_codec_preserves_old_json_and_round_trips_graph(tracked):
    """New optional lineage never changes retained operations or their JSON bytes."""
    from fabricops_kit.config.metadata_schemas import decode_metadata_row, encode_metadata_row
    t = tracked
    graph, _ = t.write(t.spark.range(1).selectExpr('id + 1 AS out'))
    operation = {'operation_key': 'target:output', 'table_id': 'output', 'asset_type': 'TABLE',
        'asset_workspace_id': 'physical', 'pipeline_role': 'target', 'destination': {'kind': 'lakehouse', 'item_id': 'lakehouse', 'table_name': 'output'},
        'source_assets': [], 'status': 'succeeded', 'stages': []}
    before = {'run_schema_version': 4, 'operations': json.dumps([operation], indent=2)}
    assert encode_metadata_row('METADATA_PIPELINE_RUN', before) == before
    assert 'lineage' not in decode_metadata_row('METADATA_PIPELINE_RUN', before)['operations'][0]
    operation['lineage'] = graph
    physical = encode_metadata_row('METADATA_PIPELINE_RUN', {'run_schema_version': 4, 'operations': [operation]})
    decoded = decode_metadata_row('METADATA_PIPELINE_RUN', physical)
    assert decoded['operations'][0]['lineage']['status'] == 'complete'
    assert decoded["operations"][0]["lineage"]["outputs"][0]["column_name"] == "out"


def test_pandas_round_trip_retains_participation_but_has_no_fabricated_roots(tracked):
    """Exercise the actual conversion users and generated notebooks can perform."""
    pytest.importorskip('pandas')
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, amount long'), 'a')
    pandas_frame = a.toPandas()
    pandas_frame['amount'] *= 3
    rebuilt = t.spark.createDataFrame(pandas_frame)
    graph, _ = t.write(rebuilt)
    assert graph['status'] == 'unknown'
    assert roots(graph, 'amount') == set()
    assert 'a' in t.plan.runtime_context['_pipeline_bindings']


def test_explode_and_sql_views_preserve_dependencies(tracked):
    """Traverse native generator and SQL expressions over registered sources."""
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, [2, 3])], 'id long, values array<long>'), 'a')
    a.createOrReplaceTempView('lineage_test_view')
    try:
        result = t.spark.sql('SELECT id, explode(values) AS value FROM lineage_test_view')
        graph, _ = t.write(result)
        assert graph['status'] == 'complete', graph
        assert roots(graph, 'value') == {('a', 'values')}
        assert 'Generate' in {node['operation'] for node in graph['nodes']}
    finally:
        t.spark.catalog.dropTempView('lineage_test_view')


def test_graph_limits_are_explicit_and_cannot_fail_writes(tracked, monkeypatch):
    """A partial graph must never silently omit outputs or claim completeness."""
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, amount long'), 'a')
    monkeypatch.setattr(lineage, '_LINEAGE_MAX_NODES', 1)
    graph, fragment = t.write(a)
    assert fragment is None
    assert graph['status'] == 'unknown' and graph['gaps'] == ['lineage_limit']
    assert graph['output_count'] == 2 and graph['omitted_output_count'] == 0
    monkeypatch.setattr(lineage, '_LINEAGE_MAX_OUTPUTS', 1)
    graph, _ = t.write(a)
    assert graph['output_count'] == 2 and graph['omitted_output_count'] == 1


def test_runtime_without_jvm_plan_records_unknown(tracked):
    """Unsupported Spark runtimes retain a diagnostic rather than breaking publication."""
    graph, fragment = tracked.write(SimpleNamespace(columns=['out']))
    assert fragment is None
    assert graph['outputs'][0]['gaps'] == ['plan_access_unavailable']


def test_run_finalization_retains_graph_and_projection_status(runtime, spark_session):
    """Persist the captured graph through the actual Run journal and failure finalization."""
    from fabricops_kit.pipeline import shared
    make, operation, saved, _, _ = runtime
    plan = make(mode='ungoverned', roles=('source', 'target'))
    operation(plan, 0)
    a = spark_session.createDataFrame([(1, 5)], 'id long, amount long')
    lineage.register_read_lineage(plan, {'table_id': 'table0', 'dataframe': a})
    operation(plan, 1)
    lineage.capture_write_lineage(a.selectExpr('amount * 2 AS result'), context={'execution_plan': plan},
        table_id='table1', write_mode='overwrite')
    plan.evidence['operations']['target:asset1']['publication_status'] = 'published'
    plan.evidence['boundary_completed'] = False
    record = shared.finalize_pipeline_run(plan, failed=True)
    retained = saved[plan.plan_id]
    assert retained['operations'][1]['lineage']['status'] == 'complete'
    rows = lineage.column_lineage_rows(record)
    assert any(row['source_table_id'] == 'table0' and row['source_column_name'] == 'amount'
               and row['target_column_name'] == 'result' and 'VALUE' in row['dependency_types'] for row in rows)
    assert all(row['run_id'] == plan.plan_id and row['publication_status'] == 'published' for row in rows)


def test_ambiguous_read_never_picks_a_physical_asset(tracked):
    """Equivalent plans registered under conflicting identities are not trustworthy."""
    t = tracked
    a = t.spark.createDataFrame([(1,)], 'id long')
    t.read(a, 'first')
    t.read(a, 'second')
    graph, _ = t.write(a)
    assert graph['status'] == 'unknown'
    assert graph['outputs'][0]['gaps'] == ['ambiguous_read']
    assert roots(graph, 'id') == set()


def test_partial_branch_and_discarded_udf_do_not_poison_known_columns(tracked):
    """Coverage follows actual output ancestors rather than all intermediate expressions."""
    from pyspark.sql import functions as F
    t = tracked
    a = t.read(t.spark.createDataFrame([(1, 2)], 'id long, amount long'), 'a')
    opaque = F.udf(lambda value: value, 'long')
    graph, _ = t.write(a.withColumn('discarded', opaque('amount')).select('amount'))
    assert graph['status'] == 'complete'
    assert 'PythonUDF' not in {node['operation'] for node in graph['nodes']}
    unknown = t.spark.createDataFrame([(3,)], 'amount long')
    graph, _ = t.write(a.select('amount').unionByName(unknown))
    assert graph['status'] == 'partial'
    assert roots(graph, 'amount') == {('a', 'amount')}
    assert graph['outputs'][0]['gaps'] == ['unregistered_or_severed_read']


def test_aggregate_filter_influence_is_not_a_value_dependency(tracked):
    """Aggregate-local predicates influence selection without supplying summed values."""
    t = tracked
    a = t.read(t.spark.createDataFrame([(2, True)], 'amount long, accepted boolean'), 'a')
    graph, _ = t.write(a.selectExpr('sum(DISTINCT amount) FILTER (WHERE accepted) AS total'))
    assert graph['status'] == 'complete'
    assert roots(graph, 'total') == {('a', 'amount')}
    assert roots(graph, 'total', 'FILTER') == {('a', 'accepted')}
    assert any(node['operation'] == 'AggregateExpression' and node.get('name') == 'DISTINCT' for node in graph['nodes'])
