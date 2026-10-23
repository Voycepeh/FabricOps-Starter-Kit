"""Build a deployment wheel with an administrator-reviewed, pinned registry locator."""
import argparse
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from uuid import UUID


def main():
    """Build from an isolated source copy, never editing the installed runtime package."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    locator = json.loads(args.bootstrap.read_text())
    if set(locator) != {"governance_workspace_id", "metadata_item_id", "governance_schema", "engineering_schema"}:
        parser.error("Bootstrap requires Governance Workspace ID, Metadata item ID and both ownership schemas.")
    for key in ("governance_workspace_id", "metadata_item_id"):
        UUID(locator[key])
    if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", locator[key]) for key in ("governance_schema", "engineering_schema")):
        parser.error("Metadata ownership schemas must be simple identifiers.")
    if locator["governance_schema"] == locator["engineering_schema"]:
        parser.error("Governance and engineering metadata schemas must be distinct.")
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as folder:
        project = Path(folder)
        shutil.copytree(root / "src", project / "src")
        for name in ("pyproject.toml", "README.md", "LICENSE", "LICENSE.md"):
            if not (root / name).is_file():
                continue
            shutil.copy2(root / name, project / name)
        (project / "src/fabricops_kit/config/registry_bootstrap.json").write_text(json.dumps(locator, indent=2) + "\n")
        subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(args.output.resolve()), str(project)], check=True)


if __name__ == "__main__":
    main()
