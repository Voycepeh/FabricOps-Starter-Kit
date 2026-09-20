"""Architecture checks for ordinary Fabric I/O routing."""

from __future__ import annotations

import ast
from pathlib import Path


SOURCE_ROOT = Path("src/fabricops_kit")
LOW_LEVEL_TRANSPORT_HELPERS = {
    "read_delta_path",
    "read_csv_path",
    "read_json_path",
    "read_excel_file",
    "read_warehouse_synapsesql",
    "read_sql_endpoint_query_core",
    "write_delta_path",
    "write_warehouse_synapsesql",
}


def test_non_io_modules_do_not_import_low_level_read_write_transport() -> None:
    """Keep reusable physical read/write transport behind foundational I/O owners."""
    violations: list[str] = []
    for path in SOURCE_ROOT.rglob("*.py"):
        if SOURCE_ROOT / "io" in path.parents:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            if node.module != "fabricops_kit.io.shared" and not node.module.endswith(".io.shared"):
                continue
            imported = {alias.name for alias in node.names}
            blocked = sorted(imported & LOW_LEVEL_TRANSPORT_HELPERS)
            if blocked:
                violations.append(f"{path}:{node.lineno}: {', '.join(blocked)}")

    assert not violations, (
        "Ordinary Fabric reads/writes must use foundational I/O owner functions: "
        + "; ".join(violations)
    )
