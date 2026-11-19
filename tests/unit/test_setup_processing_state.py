"""Processing State setup transitions using Spark data and isolated Delta I/O."""
from importlib import import_module
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared as processing_state
from tests.helpers import framework_config

setup = import_module("fabricops_kit.config.setup_processing_state")


class MissingPath(Exception):
    """Stand in for Spark reporting a missing Delta location."""

    def getCondition(self):
        """Return the Spark error condition."""
        return "PATH_NOT_FOUND"


def test_setup_creates_empty_state_once(monkeypatch):
    """Use the configured Files path and preserve the existing store on reruns."""
    config = framework_config()
    context = {"config": config, "scope_workspace_id": "dev"}
    destination = processing_state.processing_state_path(context)
    frame = SimpleNamespace(schema=processing_state.processing_state_schema())
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

    assert setup.setup_processing_state(config=config, workspace_id="dev") == {
        "status": "created", "path": "Files/fabricops/misc/processing_state",
    }
    assert setup.setup_processing_state(config=config, workspace_id="dev")["status"] == "validated"
    assert tables == {destination: frame}


def test_missing_state_fails_runtime_read_with_setup_guidance(monkeypatch):
    """Distinguish an absent store from a legitimate empty snapshot."""
    def missing(*_args, **_kwargs):
        raise MissingPath()

    monkeypatch.setattr(processing_state, "get_spark_session", lambda **kwargs: object())
    monkeypatch.setattr(processing_state, "read_delta_path", missing)
    with pytest.raises(RuntimeError, match=r"run setup_processing_state\(\)"):
        processing_state.read_processing_state(context={"config": framework_config(), "scope_workspace_id": "dev"})


def test_permission_failure_does_not_create_an_empty_store(monkeypatch):
    """Preserve permission errors instead of initializing state."""
    def deny(*_args, **_kwargs):
        raise PermissionError("Read forbidden")

    monkeypatch.setattr(setup, "get_spark_session", lambda: object())
    monkeypatch.setattr(setup, "read_delta_path", deny)
    monkeypatch.setattr(setup, "write_delta_path", lambda *a, **kw: pytest.fail("must not write"))
    with pytest.raises(PermissionError, match="Read forbidden"):
        setup.setup_processing_state(config=framework_config(), workspace_id="dev")
