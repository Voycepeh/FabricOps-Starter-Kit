import subprocess
import sys

from scripts.check_release_ready import get_init_version, get_pyproject_version


def test_repo_versions_match():
    from fabricops_kit import __version__

    with open("pyproject.toml", "r", encoding="utf-8") as handle:
        pyproject_text = handle.read()

    assert get_pyproject_version(pyproject_text) == __version__


def test_release_ready_script_runs():
    result = subprocess.run(
        [sys.executable, "scripts/check_release_ready.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_version_parsers_smoke():
    assert get_pyproject_version('[project]\nversion = "1.2.3"\n') == "1.2.3"
    assert get_init_version('__version__ = "1.2.4"\n') == "1.2.4"
