"""Tests for the packaged FabricOps Context Layer."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re

import pytest

import fabricops_kit
from fabricops_kit import FabricOpsContextLayer


ROOT = Path(__file__).parents[2]
FROZEN_PIPELINE = ROOT / "templates" / "releases" / "v0.2.0" / "02_pipeline.ipynb"
FROZEN_ENV = ROOT / "templates" / "releases" / "v0.2.0" / "00_env_config.ipynb"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_calls(path: Path) -> set[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    calls: set[str] = set()
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "\n".join(
            line for line in "".join(cell["source"]).splitlines() if not line.lstrip().startswith(("%", "!"))
        )
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    return calls


def test_context_layer_is_root_exported_and_contains_versions() -> None:
    """Expose the class and include source and installed target versions."""
    context = FabricOpsContextLayer().for_task("migrate_pipeline", from_version="0.2.0")

    assert "FabricOpsContextLayer" in fabricops_kit.__all__
    assert "Source FabricOps version: 0.2.0" in context
    assert f"Target installed FabricOps version: {fabricops_kit.__version__}" in context


@pytest.mark.parametrize(
    ("task", "from_version", "message"),
    [
        ("unknown", "0.2.0", "Unsupported Context Layer task"),
        ("migrate_pipeline", None, "from_version is required"),
        ("migrate_pipeline", "0.1.0", "Unsupported pipeline migration source version"),
    ],
)
def test_context_layer_rejects_unsupported_requests(task: str, from_version: str | None, message: str) -> None:
    """Reject unsupported tasks and versions with deterministic errors."""
    with pytest.raises(ValueError, match=message):
        FabricOpsContextLayer().for_task(task, from_version=from_version)


def test_migration_context_encodes_structural_and_ownership_contracts() -> None:
    """Encode stable pipeline structure and payload ownership rules."""
    context = FabricOpsContextLayer().for_task("migrate_pipeline", from_version="0.2.0")

    assert "Environment -> Data Contract -> Read -> Transform -> Write" in context
    assert "project-owned environment values and source/target configuration" in context
    assert "transformation/business logic" in context
    assert "before the first `pipeline_read()`" in context
    assert "before target resolution, checks, and `pipeline_write()`" in context
    assert "Never invent unsupported FabricOps APIs" in context
    assert "private/internal imports" in context
    assert "engineer review" in context


def test_recommended_fabricops_apis_are_real_root_exports() -> None:
    """Recommend only APIs present in the root surface and target template."""
    context = FabricOpsContextLayer().for_task("migrate_pipeline", from_version="0.2.0")
    api_line = next(line for line in context.splitlines() if line.startswith("Recommended public APIs"))
    recommended = set(re.findall(r"`([a-z][a-z0-9_]*)`", api_line))

    assert recommended
    assert recommended <= set(fabricops_kit.__all__)
    assert recommended <= _code_calls(ROOT / "templates" / "notebooks" / "02_pipeline.ipynb")


def test_v020_knowledge_is_pinned_to_real_immutable_fixtures() -> None:
    """Pin migration claims to structural facts and frozen fixture hashes."""
    context = FabricOpsContextLayer().for_task("migrate_pipeline", from_version="0.2.0")
    frozen_notebook = json.loads(FROZEN_PIPELINE.read_text(encoding="utf-8"))
    cell_ids = {cell["id"] for cell in frozen_notebook["cells"]}

    assert _sha256(FROZEN_ENV) in context
    assert _sha256(FROZEN_PIPELINE) in context
    assert {"environment", "contracts", "read-setup", "transform", "write-setup"} <= cell_ids
    assert "READ_MODE" not in FROZEN_PIPELINE.read_text(encoding="utf-8")
    assert "READ_MODE" in (ROOT / "templates" / "notebooks" / "02_pipeline.ipynb").read_text(encoding="utf-8")
    assert "`READ_MODE = \"full\"`" in context


def test_context_resources_are_loaded_with_importlib_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    """Load every context section through the package resource loader."""
    import fabricops_kit.context.shared as module

    loaded: list[tuple[str, ...]] = []
    original = module.FabricOpsContextLayer._read_resource

    def recording_loader(*parts: str) -> str:
        loaded.append(parts)
        return original(*parts)

    monkeypatch.setattr(module.FabricOpsContextLayer, "_read_resource", staticmethod(recording_loader))

    FabricOpsContextLayer().for_task("migrate_pipeline", from_version="0.2.0")

    assert loaded == [("fabricops.md",), ("pipeline.md",), ("migrations", "0.2.0.md")]
