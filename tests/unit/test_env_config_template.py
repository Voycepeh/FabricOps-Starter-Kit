"""Standard notebooks resolve central configuration without local environment notebooks."""
from pathlib import Path
import json


def test_standard_templates_do_not_require_local_environment_configuration():
    """Keep only governance and pipeline notebooks in the standard operating model."""
    root = Path("templates/notebooks")
    assert not (root / "00_env_config.ipynb").exists()
    for path in [*root.glob("*.ipynb"), *Path("templates/DemoData").glob("*.ipynb")]:
        notebook = json.loads(path.read_text())
        code = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code")
        assert "%run 00_env_config" not in code
        assert "PIPELINE_MODE =" not in code
        if path.name.startswith("02"):
            assert "pipeline = setup_pipeline()" in code
            assert "finalize_pipeline()" in code
