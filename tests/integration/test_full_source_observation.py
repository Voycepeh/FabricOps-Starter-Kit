"""Read scope and optional observation remain independent."""
# ruff: noqa: D103
from importlib import import_module
from types import SimpleNamespace
import pytest
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.mark.parametrize("store_type", ["lakehouse", "warehouse"])
@pytest.mark.parametrize("has_data", [True, False])
def test_incremental_read_does_not_trigger_optional_source_observation(spark_session, monkeypatch, store_type, has_data):
    read = import_module("fabricops_kit.pipeline.pipeline_read")
    import fabricops_kit.io as io
    source = spark_session.createDataFrame([(1, "a"), (2, "b")], "id int, value string")
    identity = dict(table_id="source", table_name="source", store="Bronze", store_type=store_type, schema="dbo")
    monkeypatch.setattr(read, "resolve_physical_table_identity", lambda *a, **kw: identity)
    monkeypatch.setattr(read, "resolve_pipeline_data_contract", lambda *a, **kw: None)
    monkeypatch.setattr(read, "capture_source_observation", lambda **kw: [])
    monkeypatch.setattr(read, "resolve_incremental_source_scope", lambda **kw:
                        dict(type="incremental", column="id", after=1, through=2, has_data=has_data, first_run=False))
    monkeypatch.setattr(read, "read_lakehouse_table", lambda *a, **kw: source)
    monkeypatch.setattr(read, "read_warehouse_query", lambda query, **kw: source.where("id > 1") if has_data else source.limit(0))
    monkeypatch.setattr(io, "read_warehouse_table", lambda *a, **kw: source)
    monkeypatch.setattr(shared, "observe_full_source", lambda *a, **kw: pytest.fail("Read invoked optional observation"))
    result = read.pipeline_read(store="Bronze", schema="dbo", table_name="source", read_mode="incremental",
        read_parameters={"watermark_column": "id"}, target_table_id="target", context={"config": object(), "scope_workspace_id": "workspace", "_spark_session": spark_session}, verbose=False)
    assert result["dataframe"].count() == (1 if has_data else 0)
    assert result["full_source_observation"]["status"] == "skipped"
