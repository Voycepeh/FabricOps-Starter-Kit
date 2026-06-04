import importlib
import importlib.util
import sys
import tomllib
import types
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "fabricops_kit_versioning_under_test",
    Path(__file__).resolve().parents[1] / "src" / "fabricops_kit" / "versioning.py",
)
versioning = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(versioning)


def _install_import_dependency_stubs(monkeypatch):
    jsonschema_stub = types.ModuleType("jsonschema")
    jsonschema_stub.Draft202012Validator = type("Draft202012Validator", (), {})

    pyspark_stub = types.ModuleType("pyspark")
    pyspark_sql_stub = types.ModuleType("pyspark.sql")
    pyspark_functions_stub = types.ModuleType("pyspark.sql.functions")
    pyspark_window_stub = types.ModuleType("pyspark.sql.window")
    pyspark_sql_stub.SparkSession = type("SparkSession", (), {})
    pyspark_sql_stub.functions = pyspark_functions_stub
    pyspark_window_stub.Window = type("Window", (), {})

    for module_name, module in {
        "pandas": types.ModuleType("pandas"),
        "yaml": types.ModuleType("yaml"),
        "jsonschema": jsonschema_stub,
        "pyspark": pyspark_stub,
        "pyspark.sql": pyspark_sql_stub,
        "pyspark.sql.functions": pyspark_functions_stub,
        "pyspark.sql.window": pyspark_window_stub,
    }.items():
        monkeypatch.setitem(sys.modules, module_name, module)


def _fresh_import_fabricops_kit(monkeypatch):
    _install_import_dependency_stubs(monkeypatch)
    for module_name in list(sys.modules):
        if module_name == "fabricops_kit" or module_name.startswith("fabricops_kit."):
            monkeypatch.delitem(sys.modules, module_name, raising=False)
    return importlib.import_module("fabricops_kit")


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


def test_fabricops_version_exists_and_is_non_empty(monkeypatch):
    fabricops_kit = _fresh_import_fabricops_kit(monkeypatch)

    assert isinstance(fabricops_kit.__version__, str)
    assert fabricops_kit.__version__


def test_get_package_version_matches_fabricops_version(monkeypatch):
    fabricops_kit = _fresh_import_fabricops_kit(monkeypatch)

    assert fabricops_kit.get_package_version() == fabricops_kit.__version__


def test_pyproject_version_remains_0_1_0():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert pyproject_data["project"]["version"] == "0.1.0"


def test_importing_fabricops_kit_does_not_print(monkeypatch, capsys):
    _fresh_import_fabricops_kit(monkeypatch)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
