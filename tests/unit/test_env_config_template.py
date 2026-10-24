"""Regression tests for the shared 00_env_config notebook template."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _env_config_source() -> str:
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def test_env_config_derives_runtime_setup_from_declared_paths() -> None:
    """Changing logical store names should not require edits later in the notebook."""
    source = _env_config_source()

    assert "REQUIRED_TARGETS =" not in source
    assert 'CONFIG.path_config.paths[ENV]["source"]' not in source
    assert "ACTIVE_STORE" not in source
    assert "setup_notebook(" not in source
    assert "notebookutils.notebook.exit(json.dumps(" in source


def test_env_config_leaves_metadata_schema_routing_to_framework() -> None:
    """Canonical metadata writers should own governance versus engineering schema routing."""
    source = _env_config_source()

    assert "    metadata_schema=" not in source
    assert "VALIDATION_MODE" not in source
    assert '"notebook_context"' not in source
    assert "builtins.FABRIC_CONTEXT" not in source
    assert '"config": asdict(CONFIG)' in source
    assert "governance_metadata_schema" in source
    assert "engineering_metadata_schema" in source


def test_env_config_optional_dropdowns_use_supported_widget_type() -> None:
    """Starter custom dropdown fields should render as dropdown controls."""
    source = _env_config_source()

    assert source.count('"key": "optional_dropdown"') == 2
    assert source.count('"type": "dropdown"') == 2
    assert '"type": "select"' not in source



def _path_config_source():
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text())
    return next("".join(cell["source"]) for cell in notebook["cells"] if "ENV_ITEMS = {" in "".join(cell["source"]))


def _substituted_config_source(unresolved=None):
    import re
    return re.sub(r"<[A-Z_]+>", lambda match: match[0] if match[0] == unresolved else "example_" + match[0][1:-1], _path_config_source())


def test_generic_config_preserves_physical_names_and_metadata_routing():
    """Example item names survive construction alongside central Metadata routing."""
    from fabricops_kit import FabricStore, PathConfig
    namespace = {"FabricStore": FabricStore, "PathConfig": PathConfig}
    exec(compile(_substituted_config_source(), "<00_env_config>", "exec"), namespace)
    for env in ("dev", "test", "prod"):
        stores = namespace["PATH_CONFIG"].paths[env]
        assert stores["Gold"].name == "example_GOLD_NAME"
        assert stores["Gold"].item_id == "example_GOLD_ITEM_ID"
        assert stores["Gold"].workspace_id == "example_" + env.upper() + "_WORKSPACE_ID"
        assert stores["Metadata"].schema == "governance"
        assert stores["Metadata"].workspace_id == "example_GOVERNANCE_WORKSPACE_ID"


@pytest.mark.parametrize("unresolved", ["<DEV_WORKSPACE_ID>", "<GOLD_NAME>", "<GOLD_ITEM_ID>",
                                        "<GOVERNANCE_WORKSPACE_ID>", "<METADATA_ITEM_ID>"])
def test_generic_config_rejects_placeholders_before_io(unresolved):
    """Unresolved deployment values fail during configuration construction."""
    from fabricops_kit import FabricStore, PathConfig
    with pytest.raises(ValueError, match="actual Fabric value"):
        exec(compile(_substituted_config_source(unresolved), "<00_env_config>", "exec"),
             {"FabricStore": FabricStore, "PathConfig": PathConfig})


def test_generic_config_supports_one_custom_environment_and_store():
    """Example environment and layer names impose no mandatory topology."""
    from fabricops_kit import FabricStore, PathConfig
    source = _substituted_config_source()
    boundary = source.index("def _required_config_value")
    namespace = {"FabricStore": FabricStore, "PathConfig": PathConfig}
    exec(source[:boundary], namespace)
    namespace["ENGINEERING_WORKSPACES"] = {"poc": "custom_workspace"}
    namespace["ENV_ITEMS"] = {"poc": {"Product": {"name": "wh_Custom", "item_id": "custom_item", "kind": "warehouse"}}}
    exec(source[boundary:], namespace)
    assert set(namespace["PATH_CONFIG"].paths) == {"poc"}
    assert set(namespace["PATH_CONFIG"].paths["poc"]) == {"Product", "Metadata"}


def test_generic_template_contains_no_deployment_identifiers_or_saved_outputs():
    """Published configuration is independent of personal Fabric resources."""
    import re
    path = Path("templates/notebooks/00_env_config.ipynb")
    notebook = json.loads(path.read_text())
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", json.dumps({"source": _env_config_source(), "metadata": notebook["metadata"]}), re.I)
    assert "ODI" not in path.read_text()
    assert all(not cell.get("outputs") for cell in notebook["cells"])
    assert 'caller_workspace_id = ""' in _env_config_source()
    assert 'INITIALIZE_METADATA = False' in _env_config_source()
