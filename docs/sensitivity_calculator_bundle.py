"""Bundle the checkout's FabricOps source for browser assessments."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def on_post_build(config):
    """Package the current source alongside the generated site."""
    root = Path(__file__).resolve().parent.parent
    package = root / "src" / "fabricops_kit"
    output = Path(config.site_dir) / "assets" / "sensitivity-calculator.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as bundle:
        for source in sorted(package.rglob("*.py")):
            bundle.write(source, source.relative_to(root).as_posix())
        bundle.write(root / "pyproject.toml", "pyproject.toml")
        bundle.write(root / "docs" / "_tools" / "sensitivity_calculator.py", "sensitivity_calculator.py")
