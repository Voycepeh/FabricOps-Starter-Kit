"""Architecture contract for physical Fabric I/O ownership."""

from __future__ import annotations

import ast
from pathlib import Path


SOURCE_ROOT = Path("src/fabricops_kit")


def _outside_io_sources():
    return [path for path in SOURCE_ROOT.rglob("*.py") if SOURCE_ROOT / "io" not in path.parents]


def test_non_io_modules_do_not_import_io_shared() -> None:
    """Keep the low-level shared implementation private to the I/O package."""
    violations = []
    for path in _outside_io_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "fabricops_kit.io.shared" or node.module.endswith(".io.shared"):
                    violations.append(f"{path}:{node.lineno}")
    assert not violations, "io.shared is implementation-only for src/fabricops_kit/io/: " + ", ".join(violations)


def test_non_io_modules_do_not_own_physical_fabric_calls() -> None:
    """Keep raw physical persistence calls inside the I/O package."""
    violations = []
    for path in _outside_io_sources():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            rendered = ast.unparse(node.func)
            forbidden = (
                rendered.endswith("DeltaTable.forPath"),
                rendered.endswith(".synapsesql"),
                rendered.endswith(".save"),
            )
            raw_delta_load = rendered.endswith(".load") and "spark.read.format" in ast.unparse(node)
            if any(forbidden) or raw_delta_load:
                violations.append(f"{path}:{node.lineno}:{rendered}")
    assert not violations, "physical Fabric I/O must be owned by src/fabricops_kit/io/: " + ", ".join(violations)
