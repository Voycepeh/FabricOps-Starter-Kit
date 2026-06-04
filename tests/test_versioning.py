import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "fabricops_kit_versioning_under_test",
    Path(__file__).resolve().parents[1] / "src" / "fabricops_kit" / "versioning.py",
)
versioning = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(versioning)


def test_docs_version_maps_patch_versions_to_major_minor_docs():
    assert versioning.get_docs_version("1.0.0") == "1.0"
    assert versioning.get_docs_version("1.0.2") == "1.0"
    assert versioning.get_docs_version("1.1.0") == "1.1"


def test_unknown_version_falls_back_to_latest_docs():
    assert versioning.get_docs_version("unknown") == "latest"
    assert versioning.get_docs_url("unknown") == "https://voycepeh.github.io/FabricOps-Starter-Kit/latest/"


def test_docs_url_maps_package_version_to_major_minor_docs():
    assert versioning.get_docs_url("1.0.2") == "https://voycepeh.github.io/FabricOps-Starter-Kit/1.0/"


def test_release_notes_url_uses_patch_specific_version():
    assert (
        versioning.get_release_notes_url("1.0.2")
        == "https://voycepeh.github.io/FabricOps-Starter-Kit/latest/releases/v1.0.2/"
    )


def test_print_runtime_banner_does_not_crash(monkeypatch, capsys):
    monkeypatch.setattr(versioning, "get_package_version", lambda: "1.0.2")

    versioning.print_runtime_banner()

    output = capsys.readouterr().out
    assert "Installed package version: 1.0.2" in output
    assert "https://voycepeh.github.io/FabricOps-Starter-Kit/1.0/" in output
