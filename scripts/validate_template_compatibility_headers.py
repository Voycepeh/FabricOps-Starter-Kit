#!/usr/bin/env python3
"""Insert and validate tested-release headers in maintained notebook templates."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "notebooks"
TEMPLATE_NAMES = (
    "00_env_config.ipynb",
    "01_agreement.ipynb",
    "02_pipeline.ipynb",
    "03_governance.ipynb",
    "99_explore.ipynb",
)
HEADER_MARKER = "## Tested with FabricOps"
HEADER_SOURCE = [
    "## Tested with FabricOps\n",
    "\n",
    "This notebook template is maintained separately from FabricOps package releases. The table below records the FabricOps releases that have been manually tested with this template in Microsoft Fabric.\n",
    "\n",
    "| FabricOps release  | Tested by | Date tested | \n",
    "|---|---|---| \n",
    "| v0.1.0 |  Voyce| 13 Jul 2026 | \n",
]
RELEASE_COMMENT = "    # FabricOps v0.1.0 onwards\n"


def cell_source(cell: dict[str, object]) -> str:
    """Return a notebook cell source as text."""
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def load_notebook(path: Path) -> dict[str, object]:
    """Load one notebook as JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_base_notebook(relative_path: Path, base_ref: str) -> dict[str, object]:
    """Load one notebook from a Git reference."""
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{relative_path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def compatibility_cell(existing: dict[str, object] | None = None) -> dict[str, object]:
    """Return the canonical compatibility Markdown cell."""
    cell = deepcopy(existing) if existing is not None else {"cell_type": "markdown", "metadata": {}}
    cell["cell_type"] = "markdown"
    cell["source"] = HEADER_SOURCE
    cell.setdefault("metadata", {})
    return cell


def annotate_imports(cell: dict[str, object]) -> None:
    """Annotate each FabricOps import block with its verified release boundary."""
    source = cell.get("source")
    if not isinstance(source, list):
        return
    updated: list[str] = []
    for index, line in enumerate(source):
        updated.append(line)
        if line.strip() != "from fabricops_kit import (":
            continue
        next_line = source[index + 1] if index + 1 < len(source) else ""
        if next_line != RELEASE_COMMENT:
            updated.append(RELEASE_COMMENT)
    cell["source"] = updated


def update_notebook(notebook: dict[str, object]) -> dict[str, object]:
    """Return a notebook with one canonical header and annotated imports."""
    updated = deepcopy(notebook)
    cells = updated.get("cells")
    if not isinstance(cells, list) or not cells:
        raise ValueError("Notebook must contain cells")

    header_indexes = [
        index
        for index, cell in enumerate(cells)
        if isinstance(cell, dict) and cell.get("cell_type") == "markdown" and HEADER_MARKER in cell_source(cell)
    ]
    existing = cells[header_indexes[0]] if header_indexes else None
    for index in reversed(header_indexes):
        del cells[index]
    cells.insert(1, compatibility_cell(existing))

    for cell in cells:
        if isinstance(cell, dict) and cell.get("cell_type") == "code":
            annotate_imports(cell)
    return updated


def write_notebook(path: Path, notebook: dict[str, object], original_text: str) -> None:
    """Write JSON while preserving the notebook's existing layout style."""
    has_trailing_newline = original_text.endswith("\n")
    if original_text.startswith('{"cells"'):
        rendered = json.dumps(notebook, ensure_ascii=True, separators=(",", ":"))
    else:
        first_content_line = next(line for line in original_text.splitlines()[1:] if line.strip())
        indent = len(first_content_line) - len(first_content_line.lstrip())
        rendered = json.dumps(notebook, ensure_ascii=False, indent=indent)
    if has_trailing_newline:
        rendered += "\n"
    path.write_text(rendered, encoding="utf-8")


def source_without_fabricops_import(cell: dict[str, object]) -> str:
    """Return source excluding FabricOps import blocks and release comments."""
    source = cell.get("source", "")
    lines = source if isinstance(source, list) else str(source).splitlines(keepends=True)
    remaining: list[str] = []
    in_fabricops_import = False
    for line in lines:
        if line.strip() == "from fabricops_kit import (":
            in_fabricops_import = True
            continue
        if in_fabricops_import:
            if line.strip() == ")":
                in_fabricops_import = False
            continue
        if line != RELEASE_COMMENT:
            remaining.append(line)
    return "".join(remaining)


def validate_import_cell(cell: dict[str, object], path: Path) -> None:
    """Validate FabricOps imports are annotated, unique, and syntactically valid."""
    source = cell_source(cell)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError(f"{path}: invalid Python import cell: {exc}") from exc

    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "fabricops_kit":
            imported.extend(alias.name for alias in node.names)
    if len(imported) != len(set(imported)):
        raise ValueError(f"{path}: duplicated FabricOps imports")

    lines = cell.get("source", [])
    if isinstance(lines, list):
        for index, line in enumerate(lines):
            if line.strip() == "from fabricops_kit import (":
                if index + 1 >= len(lines) or lines[index + 1] != RELEASE_COMMENT:
                    raise ValueError(f"{path}: FabricOps import block is missing the v0.1.0 release comment")


def validate_notebook(path: Path, notebook: dict[str, object], base: dict[str, object]) -> None:
    """Validate header placement and preservation of the base notebook contract."""
    cells = notebook.get("cells")
    base_cells = base.get("cells")
    if not isinstance(cells, list) or len(cells) < 2:
        raise ValueError(f"{path}: notebook must contain at least two cells")
    if not isinstance(base_cells, list):
        raise ValueError(f"{path}: base notebook cells are invalid")
    if cells[0].get("cell_type") != "markdown" or base_cells[0].get("cell_type") != "markdown":
        raise ValueError(f"{path}: first cell must remain Markdown")
    if cells[0] != base_cells[0]:
        raise ValueError(f"{path}: first Markdown cell changed")
    if cells[1].get("cell_type") != "markdown" or HEADER_MARKER not in cell_source(cells[1]):
        raise ValueError(f"{path}: compatibility header must be the second cell")

    header_count = sum(
        HEADER_MARKER in cell_source(cell)
        for cell in cells
        if isinstance(cell, dict) and cell.get("cell_type") == "markdown"
    )
    if header_count != 1:
        raise ValueError(f"{path}: expected exactly one compatibility header, found {header_count}")

    remaining = cells[:1] + cells[2:]
    if len(remaining) != len(base_cells):
        raise ValueError(f"{path}: original cell count or order changed")
    for index, (current_cell, base_cell) in enumerate(zip(remaining, base_cells, strict=True), start=1):
        current_copy = deepcopy(current_cell)
        base_copy = deepcopy(base_cell)
        if current_copy.get("cell_type") == "code" and "from fabricops_kit import" in cell_source(current_copy):
            validate_import_cell(current_copy, path)
            current_copy["source"] = source_without_fabricops_import(current_copy)
            base_copy["source"] = source_without_fabricops_import(base_copy)
        if current_copy != base_copy:
            raise ValueError(f"{path}: unrelated change detected in original cell {index}")

    if notebook.get("metadata") != base.get("metadata"):
        raise ValueError(f"{path}: notebook metadata changed")
    for key in set(notebook) | set(base):
        if key not in {"cells", "metadata"} and notebook.get(key) != base.get(key):
            raise ValueError(f"{path}: notebook field {key!r} changed")


def main() -> int:
    """Update or validate all maintained FabricOps notebook templates."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Insert or update headers and release comments")
    parser.add_argument("--base-ref", default="HEAD", help="Git reference used to verify original cell preservation")
    args = parser.parse_args()

    for name in TEMPLATE_NAMES:
        path = TEMPLATE_DIR / name
        relative_path = path.relative_to(ROOT)
        original_text = path.read_text(encoding="utf-8")
        notebook = json.loads(original_text)
        if args.write:
            notebook = update_notebook(notebook)
            write_notebook(path, notebook, original_text)
            notebook = load_notebook(path)
        base = load_base_notebook(relative_path, args.base_ref)
        validate_notebook(path, notebook, base)
        print(f"Validated {relative_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
