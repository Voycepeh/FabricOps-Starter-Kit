"""Guard against unreachable private helper creep in fabricops_kit."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "fabricops_kit"
SEARCH_ROOTS = [SRC, ROOT / "templates" / "notebooks", ROOT / "scripts", ROOT / "tests"]

PRIVATE_HELPER_ALLOWLIST = {
    "__getattr__": "Package lazy-loading hook is invoked by Python attribute access rather than by a source-level call.",
    "_load_package_version": "Package metadata fallback is invoked during module import rather than by a source-level call.",
}


def _public_exports() -> set[str]:
    """Return names exported from fabricops_kit.__all__."""
    import fabricops_kit

    return set(fabricops_kit.__all__)


def _top_level_functions() -> dict[str, Path]:
    """Collect top-level package functions by short name."""
    functions: dict[str, Path] = {}
    for path in SRC.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions[node.name] = path
    return functions


def _referenced_names() -> set[str]:
    """Collect called, loaded, and imported names across active source roots."""
    references: set[str] = set()
    for root in SEARCH_ROOTS:
        patterns = ("*.py", "*.ipynb") if root.name != "scripts" else ("*.py",)
        for pattern in patterns:
            for path in root.rglob(pattern):
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                if path.suffix == ".ipynb":
                    references.update(part for part in text.replace('"', " ").replace("'", " ").split() if part.isidentifier())
                    continue
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Name):
                            references.add(func.id)
                        elif isinstance(func, ast.Attribute):
                            references.add(func.attr)
                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                        references.add(node.id)
                    elif isinstance(node, ast.ImportFrom):
                        references.update(alias.name for alias in node.names)
                    elif isinstance(node, ast.Import):
                        references.update(alias.name.rsplit(".", 1)[-1] for alias in node.names)
    return references


def test_private_helpers_are_reachable_or_explicitly_allowlisted():
    """Fail when a private helper is neither referenced nor intentionally allowed."""
    public = _public_exports()
    functions = _top_level_functions()
    referenced = _referenced_names() | public
    dead = {
        name: str(path.relative_to(ROOT))
        for name, path in functions.items()
        if name.startswith("_") and name not in referenced and name not in PRIVATE_HELPER_ALLOWLIST
    }
    assert dead == {}
