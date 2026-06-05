import pytest

pytestmark = pytest.mark.contract
import subprocess
import sys

from scripts.check_release_ready import get_pyproject_version, version_from_tag


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
    assert version_from_tag("v1.2.4") == "1.2.4"


def test_release_info_hook_writes_nav_target(tmp_path, monkeypatch):
    import docs.gen_release_info as release_info

    monkeypatch.setenv("FABRICOPS_PACKAGE_VERSION", "1.2.3")
    monkeypatch.setenv("FABRICOPS_DOC_VERSION", "1.2.3")
    monkeypatch.setenv("FABRICOPS_GIT_SHA", "abc123")

    release_info.on_config({"docs_dir": str(tmp_path)})

    generated = tmp_path / "release-info.md"
    assert generated.exists()
    text = generated.read_text(encoding="utf-8")
    assert "Full package release version | `1.2.3`" in text
    assert "Mike documentation version | `1.2.3`" in text
    assert "Git commit SHA | `abc123`" in text
