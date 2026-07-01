"""Enforce package owner-file architecture for public FabricOps callables."""

from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOT = Path("src/fabricops_kit")

FORBIDDEN_BATCH_FILENAMES = {
    "public.py",
    "models.py",
    "classes.py",
    "adapter.py",
    "adapters.py",
    "resolver.py",
    "resolvers.py",
}

# Keep allowlists narrow and temporary. Add a TODO with the owning migration when
# an existing package cannot be moved as part of the current PR scope.
FORBIDDEN_FILENAME_ALLOWLIST: dict[str, set[str]] = {}


def _package_dirs() -> list[Path]:
    """Return first-level FabricOps package directories that contain Python files."""
    return sorted(
        path
        for path in PACKAGE_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith("__") and any(path.glob("*.py"))
    )


def _public_functions(path: Path) -> set[str]:
    """Return top-level public functions defined in a Python source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
    }


def _classes(path: Path) -> set[str]:
    """Return top-level classes defined in a Python source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.name for node in tree.body if isinstance(node, ast.ClassDef)}


def _all_exports(path: Path) -> set[str]:
    """Return literal string names listed in a package ``__all__`` assignment."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        is_all_assignment = isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        )
        if is_all_assignment:
            if not isinstance(node.value, (ast.List, ast.Tuple)):
                return set()
            return {
                item.value
                for item in node.value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
    return set()


def test_package_batches_use_public_owner_files_shared_and_init_only() -> None:
    """Verify package batches do not add broad catch-all module filenames."""
    for package_dir in _package_dirs():
        py_files = {path.name for path in package_dir.glob("*.py")}
        allowlist = FORBIDDEN_FILENAME_ALLOWLIST.get(package_dir.name, set())
        forbidden = (py_files & FORBIDDEN_BATCH_FILENAMES) - allowlist

        assert not forbidden, (
            f"{package_dir} should use one public owner file per public function, "
            f"shared.py for helpers/classes, and __init__.py for exports. "
            f"Forbidden files found: {sorted(forbidden)}"
        )


def test_public_owner_files_define_only_their_named_public_function() -> None:
    """Verify public owner files expose at most one matching public function."""
    for package_dir in _package_dirs():
        for path in package_dir.glob("*.py"):
            if path.name in {"__init__.py", "shared.py", "metadata_schemas.py", "guardrails_shared.py"}:
                continue

            public_functions = _public_functions(path)
            expected = path.stem

            assert len(public_functions) <= 1, (
                f"{path} should define at most one public function named {expected!r}. "
                f"Found: {sorted(public_functions)}"
            )
            assert public_functions <= {expected}, (
                f"{path} should only define public function {expected!r}. "
                f"Found: {sorted(public_functions)}"
            )


def test_public_owner_files_do_not_define_classes() -> None:
    """Verify public owner files keep support classes and value objects in shared.py."""
    for package_dir in _package_dirs():
        for path in package_dir.glob("*.py"):
            if path.name in {"__init__.py", "shared.py", "metadata_schemas.py", "guardrails_shared.py"}:
                continue

            assert not _classes(path), (
                f"{path} should not define classes. "
                "Move support classes/dataclasses/value objects to shared.py."
            )


def test_package_batch_classes_live_in_shared_py() -> None:
    """Verify package-level classes are defined only in package shared.py files."""
    for package_dir in _package_dirs():
        for path in package_dir.glob("*.py"):
            if path.name in {"__init__.py", "shared.py", "metadata_schemas.py", "guardrails_shared.py"}:
                continue

            assert not _classes(path), (
                f"{path} should not define classes. "
                "Package-level classes/dataclasses/value objects belong in shared.py."
            )


def test_package_init_re_exports_public_owner_functions() -> None:
    """Verify package __init__.py files are the package export surface."""
    for package_dir in _package_dirs():
        owner_public_functions: set[str] = set()
        shared_classes = _classes(package_dir / "shared.py") if (package_dir / "shared.py").exists() else set()
        for path in package_dir.glob("*.py"):
            if path.name in {"__init__.py", "shared.py", "metadata_schemas.py", "guardrails_shared.py"}:
                continue
            owner_public_functions.update(_public_functions(path))

        if not owner_public_functions and not shared_classes:
            continue

        init_path = package_dir / "__init__.py"
        assert init_path.exists(), f"{package_dir} must expose its supported surface through __init__.py."

        package_exports = _all_exports(init_path)
        assert owner_public_functions <= package_exports, (
            f"{init_path} should re-export public owner functions. "
            f"Missing: {sorted(owner_public_functions - package_exports)}"
        )


def test_existing_public_callable_packages_follow_owner_file_pattern() -> None:
    """Verify config, io, and pipeline satisfy the owner-file architecture."""
    package_names = {path.name for path in _package_dirs()}
    assert {"config", "io", "pipeline"} <= package_names


def test_public_function_architecture_guide_is_documented_and_linked() -> None:
    """Verify the maintainer guide documents and navigates the architecture rule."""
    guide_path = Path("docs/reference/public-function-architecture.md")
    guide = guide_path.read_text(encoding="utf-8")
    agents = Path("AGENTS.md").read_text(encoding="utf-8")
    mkdocs = Path("mkdocs.yml").read_text(encoding="utf-8")

    assert "# Public Function Architecture" in guide
    assert "one owner file per public function" in guide
    assert "Do not add `public.py`, `models.py`, `classes.py`" in guide
    assert "The test suite enforces this pattern." in guide
    assert str(guide_path) in agents
    assert "Public Function Architecture: reference/public-function-architecture.md" in mkdocs
