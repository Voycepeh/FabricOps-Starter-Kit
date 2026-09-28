"""Installed-distribution smoke tests for Context Layer resources."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


pytestmark = pytest.mark.contract


def test_built_wheel_contains_and_loads_context_resources(tmp_path: Path) -> None:
    """Load packaged context from an installed wheel outside the repository."""
    root = Path(__file__).parents[2]
    dist = tmp_path / "dist"
    target = tmp_path / "installed"
    outside_repo = tmp_path / "outside-repository"
    dist.mkdir()
    target.mkdir()
    outside_repo.mkdir()

    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            ".",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(dist),
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    wheel = next(dist.glob("*.whl"))

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert "fabricops_kit/context/resources/fabricops.md" in names
    assert "fabricops_kit/context/resources/pipeline.md" in names
    assert "fabricops_kit/context/resources/migrations/0.2.0.md" in names

    install = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)],
        cwd=outside_repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert install.returncode == 0, install.stdout + install.stderr

    smoke = subprocess.run(
        [
            sys.executable,
            "-c",
            "from fabricops_kit import FabricOpsContextLayer; "
            "print(FabricOpsContextLayer().for_task('migrate_pipeline', from_version='0.2.0'))",
        ],
        cwd=outside_repo,
        env={**os.environ, "PYTHONPATH": str(target)},
        text=True,
        capture_output=True,
        check=False,
    )
    assert smoke.returncode == 0, smoke.stdout + smoke.stderr
    assert "Target installed FabricOps version: 0.2.0" in smoke.stdout
    assert "Environment -> Data Contract -> Read -> Transform -> Write" in smoke.stdout
