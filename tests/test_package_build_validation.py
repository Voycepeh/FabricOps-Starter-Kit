from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract


def test_build_outputs_validate_and_include_schema_assets(tmp_path):
    pytest.importorskip("build")
    pytest.importorskip("twine")

    dist_dir = tmp_path / "dist"
    build_result = subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, build_result.stdout + build_result.stderr

    artifacts = sorted(dist_dir.iterdir())
    wheels = [path for path in artifacts if path.suffix == ".whl"]
    sdists = [path for path in artifacts if path.name.endswith(".tar.gz")]
    assert len(wheels) == 1
    assert len(sdists) == 1

    twine_result = subprocess.run(
        [sys.executable, "-m", "twine", "check", *map(str, artifacts)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert twine_result.returncode == 0, twine_result.stdout + twine_result.stderr

    with zipfile.ZipFile(wheels[0]) as wheel:
        names = set(wheel.namelist())

    assert "fabricops_kit/schemas/dataset_contract.schema.json" in names
