"""Enforce package-wide callable architecture boundaries."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "fabricops_kit"
LOWER_LAYER_NAMES = {"profile_dataframe_core"}


@dataclass(frozen=True)
class FunctionRef:
    """Function ownership metadata used by architecture checks."""

    module: str
    name: str
    node: ast.FunctionDef


def _module_name(path: Path) -> str:
    """Return the short module name for a source path."""
    return path.stem


def _public_exports() -> set[str]:
    """Return root public callable names from ``__all__``."""
    tree = ast.parse((SRC / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            return {item.value for item in node.value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)}
    raise AssertionError("fabricops_kit.__all__ was not found")


def _functions() -> dict[tuple[str, str], FunctionRef]:
    """Return top-level package functions by module/name."""
    refs: dict[tuple[str, str], FunctionRef] = {}
    for path in SRC.glob("*.py"):
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                refs[(module, node.name)] = FunctionRef(module, node.name, node)
    return refs


def _imports_by_alias(path: Path) -> dict[str, tuple[str, str]]:
    """Resolve package-local imported function aliases to module/name pairs."""
    module = _module_name(path)
    aliases: dict[str, tuple[str, str]] = {}
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            source_module = node.module
            if node.level:
                source_module = source_module.rsplit(".", 1)[-1]
            elif source_module.startswith("fabricops_kit."):
                source_module = source_module.split(".")[-1]
            else:
                continue
            for alias in node.names:
                aliases[alias.asname or alias.name] = (source_module, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("fabricops_kit."):
                    aliases[alias.asname or alias.name.split(".")[-1]] = (alias.name.split(".")[-1], "*")
    aliases[module] = (module, "*")
    return aliases


def _called_refs(path: Path, node: ast.FunctionDef, functions: dict[tuple[str, str], FunctionRef]) -> set[tuple[str, str]]:
    """Return package-local function references called from a function body."""
    current_module = _module_name(path)
    aliases = _imports_by_alias(path)
    calls: set[tuple[str, str]] = set()
    short_to_refs = {name: (module, name) for (module, name) in functions}
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        if isinstance(call.func, ast.Name):
            name = call.func.id
            if name in aliases:
                calls.add(aliases[name])
            elif (current_module, name) in functions:
                calls.add((current_module, name))
            elif name in short_to_refs:
                calls.add(short_to_refs[name])
        elif isinstance(call.func, ast.Attribute):
            owner = call.func.value
            if isinstance(owner, ast.Name) and owner.id in aliases:
                module, _name = aliases[owner.id]
                if (module, call.func.attr) in functions:
                    calls.add((module, call.func.attr))
    return calls


def _is_public(name: str, public: set[str]) -> bool:
    """Return whether a function name is a root public callable."""
    return name in public


def _is_internal(name: str) -> bool:
    """Return whether a function name is an internal helper."""
    return name.startswith("_")


def _is_lower_layer(module: str, name: str) -> bool:
    """Return whether a function belongs to the explicitly allowed lower layer."""
    return name in LOWER_LAYER_NAMES


def test_package_callables_obey_architecture_boundaries() -> None:
    """Verify public, internal, lower-layer, and utility callable boundaries repo-wide."""
    public = _public_exports()
    functions = _functions()
    violations: list[str] = []

    for path in SRC.glob("*.py"):
        module = _module_name(path)
        for (fn_module, fn_name), ref in functions.items():
            if fn_module != module:
                continue
            called = _called_refs(path, ref.node, functions)
            for callee_module, callee_name in sorted(called):
                if callee_name == "*" or (callee_module, callee_name) == (module, fn_name):
                    continue
                caller = f"{module}.{fn_name}"
                callee = f"{callee_module}.{callee_name}"
                if _is_lower_layer(module, fn_name):
                    if _is_public(callee_name, public):
                        violations.append(f"lower-layer {caller} must not call public callable {callee}")
                elif _is_public(fn_name, public):
                    if _is_public(callee_name, public):
                        violations.append(f"public callable {caller} must not call public callable {callee}")
                elif _is_internal(fn_name):
                    if _is_public(callee_name, public):
                        violations.append(f"internal helper {caller} must not call public callable {callee}")
    assert violations == []


def test_io_core_wrapper_module_is_deleted() -> None:
    """Verify Fabric IO no longer keeps a wrapper-on-wrapper io_core layer."""
    assert not (SRC / "io_core.py").exists()
