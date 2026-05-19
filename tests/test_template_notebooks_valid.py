"""Validate template notebooks are well-formed and clean for distribution."""

from pathlib import Path

import nbformat


def test_template_notebooks_are_valid_and_cleared() -> None:
    """All template notebooks should parse with nbformat and have cleared outputs."""
    notebook_paths = sorted(Path("templates/notebooks").glob("*.ipynb"))
    assert notebook_paths, "Expected at least one template notebook under templates/notebooks/."

    for path in notebook_paths:
        with path.open("r", encoding="utf-8") as handle:
            notebook = nbformat.read(handle, as_version=4)

        nbformat.validate(notebook)

        for index, cell in enumerate(notebook.cells):
            if cell.get("cell_type") != "code":
                continue
            assert cell.get("execution_count") is None, (
                f"{path} code cell {index} must have execution_count cleared."
            )
            assert cell.get("outputs") == [], f"{path} code cell {index} must have outputs cleared."
