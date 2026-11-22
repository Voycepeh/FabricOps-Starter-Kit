"""Processing State setup transitions using Spark data and isolated Delta I/O."""
from importlib import import_module
import sys
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared as processing_state
from tests.helpers import framework_config

setup = import_module("fabricops_kit.config.setup_metadata_tables")


class MissingPath(Exception):
    """Stand in for Spark reporting a missing Delta location."""

    def getCondition(self):
        """Return the Spark error condition."""
        return "PATH_NOT_FOUND"


def _stub_delta_isolation(monkeypatch, expected_path, properties):
    def for_path(spark, path):
        assert path == expected_path
        detail = SimpleNamespace(select=lambda name: SimpleNamespace(first=lambda: {name: properties}))
        return SimpleNamespace(detail=lambda: detail)

    monkeypatch.setitem(sys.modules, "delta.tables", SimpleNamespace(DeltaTable=SimpleNamespace(forPath=for_path)))


def test_setup_creates_empty_state_once(monkeypatch):
    """Use the configured Lakehouse table path and preserve the existing store on reruns."""
    config = framework_config()
    context = {"config": config, "scope_workspace_id": "dev"}
    destination = processing_state.processing_state_path(context)
    assert destination.endswith("/Tables/misc/PROCESSING_STATE")
    frame = SimpleNamespace(schema=processing_state.processing_state_schema())
    _stub_delta_isolation(monkeypatch, destination, {"delta.isolationLevel": "Serializable"})
    tables = {}

    def read(_spark, path):
        assert path == destination
        if path not in tables:
            raise MissingPath()
        return tables[path]

    def create_frame(rows, schema):
        assert rows == []
        assert schema.fieldNames() == frame.schema.fieldNames()
        return frame

    def write(value, path, *, mode, options):
        assert options == {"delta.isolationLevel": "Serializable"}
        assert path == destination and path not in tables and mode == "errorifexists"
        tables[path] = value

    monkeypatch.setattr(setup, "get_spark_session", lambda: SimpleNamespace(createDataFrame=create_frame))
    monkeypatch.setattr(setup, "read_delta_path", read)
    monkeypatch.setattr(setup, "write_delta_path", write)

    assert setup._setup_processing_state(spark=setup.get_spark_session(), context={"config": config, "scope_workspace_id": "dev"}) == {
        "status": "created", "path": "Tables/misc/PROCESSING_STATE",
    }
    assert setup._setup_processing_state(spark=setup.get_spark_session(), context={"config": config, "scope_workspace_id": "dev"})["status"] == "validated"
    assert tables == {destination: frame}


@pytest.mark.parametrize("properties", [{}, {"delta.isolationLevel": "WriteSerializable"}])
def test_setup_rejects_existing_store_without_serializable_isolation(monkeypatch, properties):
    """Check the required isolation before reporting the existing store as validated."""
    config = framework_config()
    destination = processing_state.processing_state_path({"config": config, "scope_workspace_id": "dev"})
    frame = SimpleNamespace(schema=processing_state.processing_state_schema())
    _stub_delta_isolation(monkeypatch, destination, properties)
    monkeypatch.setattr(setup, "get_spark_session", lambda: object())
    monkeypatch.setattr(setup, "read_delta_path", lambda spark, path: frame)
    monkeypatch.setattr(setup, "write_delta_path", lambda *a, **kw: pytest.fail("must not write"))
    with pytest.raises(RuntimeError, match="requires Serializable Delta isolation"):
        setup._setup_processing_state(spark=setup.get_spark_session(), context={"config": config, "scope_workspace_id": "dev"})


def test_missing_state_fails_runtime_read_with_setup_guidance(monkeypatch):
    """Distinguish an absent store from a legitimate empty snapshot."""
    def missing(*_args, **_kwargs):
        raise MissingPath()

    monkeypatch.setattr(processing_state, "get_spark_session", lambda **kwargs: object())
    monkeypatch.setattr(processing_state, "read_delta_path", missing)
    with pytest.raises(RuntimeError, match=r"run setup_metadata_tables\(\)"):
        processing_state.read_processing_state(context={"config": framework_config(), "scope_workspace_id": "dev"})


def test_permission_failure_does_not_create_an_empty_store(monkeypatch):
    """Preserve permission errors instead of initializing state."""
    def deny(*_args, **_kwargs):
        raise PermissionError("Read forbidden")

    monkeypatch.setattr(setup, "get_spark_session", lambda: object())
    monkeypatch.setattr(setup, "read_delta_path", deny)
    monkeypatch.setattr(setup, "write_delta_path", lambda *a, **kw: pytest.fail("must not write"))
    with pytest.raises(PermissionError, match="Read forbidden"):
        setup._setup_processing_state(spark=setup.get_spark_session(), context={"config": framework_config(), "scope_workspace_id": "dev"})


@pytest.mark.parametrize("fails", [False, True])
@pytest.mark.parametrize("raise_on_failure", [False, True])
def test_metadata_setup_includes_operational_state(monkeypatch, fails, raise_on_failure):
    """Bootstrap uses the configured context and includes state failure in readiness."""
    config = framework_config()
    spark = object()
    monkeypatch.setattr(setup, "get_spark_session", lambda: spark)
    monkeypatch.setattr(setup, "metadata_table_schema_registry", lambda: {})
    monkeypatch.setattr(setup, "_retired_preview_warnings", lambda **kwargs: [])
    monkeypatch.setattr(setup, "_historical_table_warnings", lambda **kwargs: [])
    calls = []

    def initialize(*, spark, context):
        calls.append(context)
        assert spark is not None
        assert context["scope_workspace_id"] == "dev"
        assert context["config"] == config
        if fails:
            raise PermissionError("State access denied")
        return {"status": "created", "path": "Tables/misc/PROCESSING_STATE"}

    monkeypatch.setattr(setup, "_setup_processing_state", initialize)
    kwargs = dict(config=config, workspace_id="dev", verbose=False, raise_on_failure=raise_on_failure)
    if fails and raise_on_failure:
        with pytest.raises(RuntimeError, match="misc.PROCESSING_STATE: PermissionError: State access denied"):
            setup.setup_metadata_tables(**kwargs)
    else:
        result = setup.setup_metadata_tables(**kwargs)
        assert result["status"] == ("failed" if fails else "ready")
        assert result["processing_state"]["status"] == ("failed" if fails else "created")
        assert result["tables"] == []
        assert result["active_metadata_table_count"] == 0
    assert len(calls) == 1
