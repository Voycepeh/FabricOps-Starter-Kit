"""Automatic profiles reuse current aggregates and cannot break operations."""
# ruff: noqa: D103, F811
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

import IPython
import pytest

from fabricops_kit import orchestrate_read, orchestrate_write, profile_table, setup_pipeline
from fabricops_kit.pipeline import shared as presentation
from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_session import runtime  # noqa: F401


@pytest.fixture
def compact_profile(spark_session):
    return spark_session.createDataFrame(
        [('amount', 'double', 1234, 1200, 34, 2.755, 100, 8.104, 12.3456, 1.2345, '1', 2., 3., 4., '9')],
        shared.PROFILE_DATAFRAME_COLUMNS,
    )


def test_fallback_formats_canonical_metrics_without_changing_values(compact_profile, monkeypatch, capsys):
    import IPython.display
    html_display = Mock()
    monkeypatch.setattr(IPython.display, 'display', html_display)
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    preview = presentation.capture_profile_presentation(compact_profile, scope={'profile_scope': 'full_table'})
    presentation.display_profile_presentations([preview])
    html_display.assert_called_once()
    html = html_display.call_args.args[0].data
    assert 'Complete table' in capsys.readouterr().out
    assert 'amount' in html and '1,234' in html and '2.75%' in html and '12.35' in html
    assert 'Distinct % (all rows)' in html
    assert 'overflow-x:auto' in html
    assert compact_profile.first().MEAN == 12.3456


@pytest.mark.parametrize('fails', [False, True])
def test_native_display_uses_detached_rows_and_falls_back(compact_profile, monkeypatch, capsys, fails):
    display = Mock(side_effect=RuntimeError('renderer unavailable') if fails else None)
    monkeypatch.setattr(IPython, 'get_ipython', lambda: SimpleNamespace(kernel=object(), user_ns={'display': display}))
    preview = presentation.capture_profile_presentation(compact_profile, scope={'profile_scope': 'full_table'})
    presentation.display_profile_presentations([preview])
    display.assert_called_once()
    rendered = display.call_args.args[0]
    assert rendered is not compact_profile
    assert rendered.first()['Rows'] == '1,234'
    output = capsys.readouterr().out
    assert 'Statistical profile' in output
    assert 'Statistical profile display unavailable' not in output


def test_preview_has_row_and_cell_bounds(compact_profile):
    from pyspark.sql import functions as F
    wide = compact_profile.crossJoin(compact_profile.sparkSession.range(110)).drop('id')
    wide = wide.withColumn('MIN_VALUE', F.lit('x' * 10000))
    preview = presentation.capture_profile_presentation(wide, scope={'profile_scope': 'bounded_selection', 'profiling_max_rows': 50}, dry_run=True)
    assert len(preview['rows']) == 100
    assert max(len(cell) for row in preview['rows'] for cell in row) == 120
    assert 'First 100 columns' in preview['title']
    assert 'at most 50 rows' in preview['title'] and 'not the entire table' in preview['title']
    assert 'Dry Run (not persisted)' in preview['title']


def test_capture_and_output_errors_are_nonfatal(monkeypatch):
    broken = Mock()
    broken.columns = []
    broken.select.side_effect = RuntimeError('collect unavailable')
    assert presentation.capture_profile_presentation(broken, scope={'profile_scope': 'full_table'}) is None
    monkeypatch.setattr('builtins.print', Mock(side_effect=OSError('closed output')))
    presentation.display_profile_presentations([None, {'title': 'profile'}])


def test_standalone_automatically_presents_once_at_verbose_false(spark_session, monkeypatch, capsys):
    source = spark_session.createDataFrame([(1,), (2,)], ['id'])
    calculate = Mock(wraps=shared.build_profile_dataframe)
    monkeypatch.setattr(shared, 'build_profile_dataframe', calculate)
    result = profile_table(dataframe=source, verbose=False)
    assert set(result) == {'profile', 'frequency_profile', 'row_count'}
    assert result['frequency_profile'] is None
    calculate.assert_called_once_with(source)
    output = capsys.readouterr().out
    assert output.count('Statistical profile') == 1
    assert 'Supplied DataFrame' in output
    assert 'Dry Run' not in output
    assert result['profile'].first().ROW_COUNT == 2


@pytest.mark.parametrize('mode', ['Dry Run', 'Ungoverned'])
@pytest.mark.parametrize('operation', ['read', 'write'])
def test_public_orchestration_summary_precedes_current_profile(runtime, compact_profile, monkeypatch, capsys, mode, operation):
    setup_pipeline(pipeline_mode=mode)
    for owner in (runtime.read, runtime.write):
        monkeypatch.setattr(owner, 'schedule_table_profiling', shared.schedule_table_profiling)
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {})
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: {
        'table_id': 'orders', 'store_kind': 'lakehouse', 'store': 'Bronze', 'schema': 'demo', 'table_name': 'orders'})
    monkeypatch.setattr(shared, 'get_spark_session', lambda *a, **kw: compact_profile.sparkSession)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: runtime.frame)
    calculate = Mock(return_value=compact_profile)
    monkeypatch.setattr(shared, 'build_profile_dataframe', calculate)
    persisted = Mock(return_value={'profile': compact_profile.cache(), 'frequency_profile': None, 'row_count': 1234})
    monkeypatch.setattr(shared, '_persist_profile_observation', persisted)
    runtime.publication.return_value = {'published': True, 'table_id': 'orders', 'status': 'passed'}
    capsys.readouterr()
    if operation == 'read':
        result = orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    else:
        result = orchestrate_write(runtime.frame, store='Bronze', schema='demo', table_name='orders', write_mode='overwrite')
    output = capsys.readouterr().out
    assert output.index(f'FabricOps {operation.upper()} Summary') < output.index('Statistical profile')
    assert output.count('Statistical profile') == 1
    assert ('Dry Run (not persisted)' in output) is (mode == 'Dry Run')
    assert ('Complete table' in output) is (mode != 'Dry Run' or operation == 'read')
    calculate.assert_called_once()
    assert persisted.call_count == (mode == 'Ungoverned')
    assert result['profile_result']['activities']['grain']['status'] == 'skipped'
    assert result['profile_result']['activities']['frequency']['status'] == 'skipped'
    if mode == 'Ungoverned':
        assert not compact_profile.is_cached


@pytest.mark.parametrize('mode', ['Dry Run', 'Ungoverned'])
@pytest.mark.parametrize('disabled', [False, True])
def test_skipped_profiles_have_no_calculation_or_presentation(runtime, monkeypatch, capsys, mode, disabled):
    session = setup_pipeline(pipeline_mode=mode, profiling_enabled=not disabled)
    monkeypatch.setattr(runtime.read, 'schedule_table_profiling', shared.schedule_table_profiling)
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {'standard': {'last_success': datetime.now(UTC).isoformat()}})
    calculate = Mock(side_effect=AssertionError('no physical calculation permitted'))
    monkeypatch.setattr(shared, 'execute_table_profile', calculate)
    result = orchestrate_read(store='Bronze', schema='demo', table_name='orders')
    assert result['profile_result']['activities']['standard']['status'] == 'skipped'
    assert session.plan.evidence['profiling']
    calculate.assert_not_called()
    assert 'Statistical profile' not in capsys.readouterr().out


def test_presentation_reuses_materialized_profile_without_source_scan(spark_session):
    accumulator = spark_session.sparkContext.accumulator(0)
    def record(value):
        accumulator.add(1)
        return (value,)
    source = spark_session.createDataFrame(spark_session.sparkContext.parallelize([1, 2, 3], 1).map(record), 'id long')
    profile = shared.build_profile_dataframe(source).cache()
    try:
        profile.count()  # Existing profiling/persistence action, before presentation.
        calculated = accumulator.value
        assert calculated > 0
        preview = presentation.capture_profile_presentation(profile, scope={'profile_scope': 'full_table'})
        presentation.display_profile_presentations([preview])
        assert accumulator.value == calculated
    finally:
        profile.unpersist()


def test_persisted_profile_uses_existing_canonical_metric_names(compact_profile):
    renamed = compact_profile
    for raw, persisted, _, _ in presentation._METRICS:
        renamed = renamed.withColumnRenamed(raw, persisted)
    preview = presentation.capture_profile_presentation(renamed, scope={'profile_scope': 'full_table'})
    assert preview['rows'][0][0:3] == ('amount', 'double', '1,234')
    assert preview['rows'][0][8] == '12.35'


def test_bounded_standalone_labels_only_selected_rows(spark_session, capsys):
    source = spark_session.createDataFrame([(1,), (2,), (3,)], ['id'])
    result = profile_table(dataframe=source, verbose=False, context={
        '_profile_scope': {'profile_scope': 'bounded_selection', 'profiling_max_rows': 1}})
    assert result['profile'].first().ROW_COUNT == 1
    output = capsys.readouterr().out
    assert 'Bounded selection (at most 1 rows); not the entire table' in output
    assert 'Complete table' not in output


@pytest.mark.parametrize('profiling_fails', [False, True])
def test_display_failure_preserves_committed_write_and_profiling_failures(runtime, compact_profile, monkeypatch, capsys, profiling_fails):
    setup_pipeline(pipeline_mode='Ungoverned')
    monkeypatch.setattr(runtime.write, 'schedule_table_profiling', shared.schedule_table_profiling)
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {})
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: {
        'table_id': 'orders', 'store_kind': 'lakehouse', 'store': 'Bronze', 'schema': 'demo', 'table_name': 'orders'})
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: runtime.frame)
    monkeypatch.setattr(shared, 'build_profile_dataframe', Mock(return_value=compact_profile))
    monkeypatch.setattr(compact_profile, 'select', Mock(side_effect=RuntimeError('presentation unavailable')))
    persist = Mock(side_effect=RuntimeError('profiling unavailable') if profiling_fails else None,
                   return_value={'profile': compact_profile, 'frequency_profile': None, 'row_count': 1234})
    monkeypatch.setattr(shared, '_persist_profile_observation', persist)
    runtime.publication.return_value = {'published': True, 'table_id': 'orders', 'status': 'passed'}
    if profiling_fails:
        with pytest.raises(RuntimeError, match='profiling unavailable') as error:
            orchestrate_write(runtime.frame, store='Bronze', schema='demo', table_name='orders', write_mode='overwrite')
        assert error.value.published is True
    else:
        result = orchestrate_write(runtime.frame, store='Bronze', schema='demo', table_name='orders', write_mode='overwrite')
        assert result['published'] is True
        assert result['profile_result']['activities']['standard']['status'] == 'passed'
    persist.assert_called_once()
    assert 'Statistical profile' not in capsys.readouterr().out


def test_generic_ipython_display_uses_html_fallback(compact_profile, monkeypatch, capsys):
    import IPython.display
    generic_display = Mock()
    monkeypatch.setattr(IPython.display, 'display', generic_display)
    monkeypatch.setattr(IPython, 'get_ipython', lambda: SimpleNamespace(kernel=object(), user_ns={'display': generic_display}))
    preview = presentation.capture_profile_presentation(compact_profile, scope={'profile_scope': 'full_table'})
    presentation.display_profile_presentations([preview])
    generic_display.assert_called_once()
    html = generic_display.call_args.args[0].data
    assert 'amount' in html and '1,234' in html
    assert 'DataFrame[' not in html
    assert 'overflow-x:auto' in html


def test_fabric_display_wrapped_in_ipython_module_is_used(compact_profile, monkeypatch, capsys):
    display = Mock()
    display.__module__ = "IPython.fabric_renderer"
    monkeypatch.setattr(IPython, 'get_ipython', lambda: SimpleNamespace(user_ns={'display': display}))
    preview = presentation.capture_profile_presentation(compact_profile, scope={'profile_scope': 'full_table'})
    presentation.display_profile_presentations([preview])
    display.assert_called_once()
    assert display.call_args.args[0].first()['Rows'] == '1,234'
    assert 'amount' not in capsys.readouterr().out


def test_native_display_from_builtins_without_notebook_kernel(compact_profile, monkeypatch, capsys):
    import builtins
    display = Mock()
    monkeypatch.setattr(builtins, 'display', display, raising=False)
    monkeypatch.setattr(IPython, 'get_ipython', lambda: None)
    preview = presentation.capture_profile_presentation(compact_profile, scope={'profile_scope': 'full_table'})
    presentation.display_profile_presentations([preview])
    display.assert_called_once()
    assert 'amount' not in capsys.readouterr().out


def test_skipped_profile_shows_confirmed_snapshot_in_audit_timezone(spark_session, monkeypatch, capsys):
    from fabricops_kit.pipeline import shared
    persisted = spark_session.createDataFrame(
        [("workspace-1", "orders", "snapshot-1", "amount", "double", 2, 2, 0,
          0.0, 2, 100.0, 1.5, 0.5, "1", 1.25, 1.5, 1.75, "2")],
        ["workspace_id", "table_id", "profile_snapshot_id", "column_name", "data_type",
         "row_count", "non_null_count", "null_count", "null_percent", "distinct_count",
         "distinct_percent", "mean_value", "stddev_value", "min_value",
         "percentile_25_value", "median_value", "percentile_75_value", "max_value"],
    )
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: persisted)
    output = []
    shared._show_previous_table_profile(
        "orders",
        {"last_success": "2026-11-13T01:30:00+00:00", "profile_snapshot_id": "snapshot-1"},
        context={"config": {"audit_timezone": "Asia/Singapore"}, "scope_workspace_id": "workspace-1"},
        spark_session=spark_session, presentations=output,
    )
    assert len(output) == 1
    assert "Profiling skipped; showing previous state as of 2026-11-13 09:30:00" in output[0]["title"]
    assert "[Asia/Singapore]" in output[0]["title"]
    assert output[0]["rows"][0][0] == "amount"


def test_no_previous_snapshot_means_no_reused_profile(spark_session, monkeypatch):
    from fabricops_kit.pipeline import shared
    read = Mock(side_effect=AssertionError("no metadata read expected"))
    monkeypatch.setattr(shared, 'read_lakehouse_table', read)
    output = []
    shared._show_previous_table_profile(
        "orders", {"last_success": "2026-11-13T01:30:00+00:00"},
        context={"config": {"audit_timezone": "Asia/Singapore"}, "scope_workspace_id": "workspace-1"},
        spark_session=spark_session, presentations=output,
    )
    assert output == []
    read.assert_not_called()
