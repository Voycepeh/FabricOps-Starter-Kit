"""Generate deterministic public API snapshots and release comparisons."""

from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generated_artifact_metadata import update_generated_artifact_metadata


PACKAGE_ROOT = "src/fabricops_kit"
OUTPUT_PATH = ROOT / "docs/reference/_data/public-api-compatibility.json"
SCHEMA = "fabricops_public_api_compatibility_v1"
LIFECYCLE_NAMES = {
    "SUPPORTED_PUBLIC_API": "Live",
    "PREVIEW_PUBLIC_API": "Preview",
    "DISCONTINUED_PUBLIC_API": "Discontinued",
}
RELEASE_TAG = re.compile(r"v(?P<version>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
CLASSIFICATION_ORDER = {"nonbreaking": 0, "review_required": 1, "potentially_breaking": 2}


@dataclass(frozen=True)
class SourceFunction:
    """A top-level function located without importing its module."""

    module: str
    path: str
    node: ast.FunctionDef | ast.AsyncFunctionDef

    @property
    def qualified_name(self) -> str:
        """Return the source-qualified function name."""
        return f"{self.module}.{self.node.name}"


def _run_git(*args: str) -> str:
    """Return text output from one read-only Git command."""
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout


def _module_name(path: str) -> str:
    """Return a Python module name for a package source path."""
    relative = Path(path).relative_to("src").with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _parse_source(path: str, text: str) -> ast.Module:
    """Parse source with a path-aware error message."""
    return ast.parse(text, filename=path, type_comments=True)


def _literal_string_sequence(node: ast.AST) -> tuple[str, ...] | None:
    """Return a literal string list or tuple, otherwise ``None``."""
    if not isinstance(node, (ast.List, ast.Tuple)):
        return None
    values: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            return None
        values.append(element.value)
    return tuple(values)


def _export_strings(node: ast.AST, constants: Mapping[str, tuple[str, ...]]) -> tuple[str, ...] | None:
    """Resolve common static ``__all__`` expressions without executing code."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if isinstance(node, ast.Name):
        return constants.get(node.id)
    if isinstance(node, ast.Starred):
        return _export_strings(node.value, constants)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _export_strings(node.left, constants)
        right = _export_strings(node.right, constants)
        return (*left, *right) if left is not None and right is not None else None
    if isinstance(node, (ast.List, ast.Tuple)):
        values: list[str] = []
        for element in node.elts:
            resolved = _export_strings(element, constants)
            if resolved is None:
                return None
            values.extend(resolved)
        return tuple(values)
    return None


def _registry_entries(sources: Mapping[str, str]) -> tuple[dict[str, str], bool]:
    """Read lifecycle registry entries directly from source."""
    registry_path = f"{PACKAGE_ROOT}/public_api.py"
    text = sources.get(registry_path)
    if text is None:
        return {}, False
    tree = _parse_source(registry_path, text)
    entries: dict[str, str] = {}
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        target = statement.targets[0] if isinstance(statement, ast.Assign) and statement.targets else statement.target
        if not isinstance(target, ast.Name) or target.id not in LIFECYCLE_NAMES:
            continue
        values = _literal_string_sequence(statement.value)
        if values is None:
            raise ValueError(f"{registry_path}: {target.id} must be a literal string sequence")
        for qualified_name in values:
            if qualified_name in entries:
                raise ValueError(f"{registry_path}: duplicate lifecycle entry {qualified_name}")
            entries[qualified_name] = LIFECYCLE_NAMES[target.id]
    return entries, True


def _function_index(sources: Mapping[str, str]) -> dict[str, SourceFunction]:
    """Index top-level package functions from source text."""
    functions: dict[str, SourceFunction] = {}
    for path, text in sorted(sources.items()):
        if not path.endswith(".py") or not path.startswith(f"{PACKAGE_ROOT}/"):
            continue
        module = _module_name(path)
        for statement in _parse_source(path, text).body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function = SourceFunction(module=module, path=path, node=statement)
                functions[function.qualified_name] = function
    return functions


def _legacy_export_names(sources: Mapping[str, str]) -> tuple[str, ...]:
    """Return function-like package exports when no lifecycle registry exists.

    This fallback is intentionally conservative: it discovers names listed in
    package ``__all__`` assignments and resolves them only when exactly one
    package function has the same name. Lifecycle remains Unknown.
    """
    exports: set[str] = set()
    for path, text in sorted(sources.items()):
        if not path.endswith("/__init__.py") or not path.startswith(f"{PACKAGE_ROOT}/"):
            continue
        tree = _parse_source(path, text)
        constants: dict[str, tuple[str, ...]] = {}
        for statement in tree.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            if isinstance(target, ast.Name):
                values = _export_strings(statement.value, constants)
                if values is not None:
                    constants[target.id] = values
        for statement in tree.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            if not isinstance(target, ast.Name) or target.id != "__all__":
                continue
            values = _export_strings(statement.value, constants)
            if values is not None:
                exports.update(values)
    return tuple(sorted(exports))


def _absolute_import_module(package: str, statement: ast.ImportFrom) -> str | None:
    """Resolve one package ``from`` import without importing Python code."""
    if statement.level == 0:
        return statement.module
    package_parts = package.split(".")
    keep = len(package_parts) - statement.level + 1
    if keep < 1:
        return None
    base = package_parts[:keep]
    if statement.module:
        base.extend(statement.module.split("."))
    return ".".join(base)


def _verified_function_exports(
    sources: Mapping[str, str],
    functions: Mapping[str, SourceFunction],
) -> dict[str, SourceFunction]:
    """Map package attributes to functions through static ``__init__`` re-exports."""
    import_targets: dict[str, str] = {}
    for path, text in sorted(sources.items()):
        if not path.endswith("/__init__.py") or not path.startswith(f"{PACKAGE_ROOT}/"):
            continue
        package = _module_name(path)
        for statement in _parse_source(path, text).body:
            if not isinstance(statement, ast.ImportFrom):
                continue
            imported_module = _absolute_import_module(package, statement)
            if imported_module is None:
                continue
            for alias in statement.names:
                if alias.name == "*":
                    continue
                exposed_name = alias.asname or alias.name
                import_targets[f"{package}.{exposed_name}"] = f"{imported_module}.{alias.name}"

    resolved: dict[str, SourceFunction] = {}
    pending = dict(import_targets)
    while pending:
        changed = False
        for exposed_name, imported_name in tuple(pending.items()):
            function = functions.get(imported_name) or resolved.get(imported_name)
            if function is None:
                continue
            resolved[exposed_name] = function
            del pending[exposed_name]
            changed = True
        if not changed:
            break
    return resolved


def _resolve_function(
    qualified_name: str,
    functions: Mapping[str, SourceFunction],
    verified_exports: Mapping[str, SourceFunction],
) -> SourceFunction | None:
    """Resolve only exact source identities or statically verified exports."""
    return functions.get(qualified_name) or verified_exports.get(qualified_name)


def _annotation(node: ast.AST | None) -> str | None:
    """Return a stable source representation for an annotation."""
    return ast.unparse(node) if node is not None else None


def _default(node: ast.AST | None) -> str | None:
    """Return a stable source representation for a default value."""
    return ast.unparse(node) if node is not None else None


def _parameter(
    argument: ast.arg,
    kind: str,
    default: ast.AST | None = None,
    *,
    has_default: bool = False,
) -> dict[str, Any]:
    """Build one serializable parameter record."""
    return {
        "name": argument.arg,
        "kind": kind,
        "required": not has_default and kind not in {"var_positional", "var_keyword"},
        "has_default": has_default,
        "default": _default(default) if has_default else None,
        "annotation": _annotation(argument.annotation),
    }


def _parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    """Return parameters in Python binding order."""
    args = node.args
    positional = [*args.posonlyargs, *args.args]
    default_offset = len(positional) - len(args.defaults)
    parameters: list[dict[str, Any]] = []
    for index, argument in enumerate(positional):
        has_default = index >= default_offset
        default = args.defaults[index - default_offset] if has_default else None
        kind = "positional_only" if index < len(args.posonlyargs) else "positional_or_keyword"
        parameters.append(_parameter(argument, kind, default, has_default=has_default))
    if args.vararg is not None:
        parameters.append(_parameter(args.vararg, "var_positional"))
    for argument, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        parameters.append(_parameter(argument, "keyword_only", default, has_default=default is not None))
    if args.kwarg is not None:
        parameters.append(_parameter(args.kwarg, "var_keyword"))
    return parameters


def _signature(name: str, parameters: Sequence[Mapping[str, Any]], return_annotation: str | None) -> str:
    """Render a readable deterministic signature."""
    rendered: list[str] = []
    positional_only_count = sum(parameter["kind"] == "positional_only" for parameter in parameters)
    has_var_positional = any(parameter["kind"] == "var_positional" for parameter in parameters)
    keyword_marker_added = False
    for index, parameter in enumerate(parameters):
        kind = parameter["kind"]
        if kind == "keyword_only" and not has_var_positional and not keyword_marker_added:
            rendered.append("*")
            keyword_marker_added = True
        prefix = "*" if kind == "var_positional" else "**" if kind == "var_keyword" else ""
        value = f"{prefix}{parameter['name']}"
        if parameter["annotation"] is not None:
            value += f": {parameter['annotation']}"
        if parameter["has_default"]:
            value += f" = {parameter['default']}"
        rendered.append(value)
        if positional_only_count and index + 1 == positional_only_count:
            rendered.append("/")
    suffix = f" -> {return_annotation}" if return_annotation is not None else ""
    return f"{name}({', '.join(rendered)}){suffix}"


def build_snapshot(
    *,
    version: str,
    revision: str | None,
    source_kind: str,
    sources: Mapping[str, str],
) -> dict[str, Any]:
    """Build one version snapshot from package source text."""
    registry, registry_exists = _registry_entries(sources)
    functions = _function_index(sources)
    verified_exports = _verified_function_exports(sources, functions)
    lifecycle_source = "public_api_registry" if registry_exists else "legacy_package_exports"
    snapshot_certainty = "certain" if registry_exists else "uncertain"
    notes = []
    if not registry_exists:
        notes.append(
            "This source predates src/fabricops_kit/public_api.py. APIs are inferred from package __all__ exports; "
            "lifecycle is Unknown and comparisons require review."
        )
        names: dict[str, str] = {}
        by_name: dict[str, list[SourceFunction]] = {}
        for function in functions.values():
            by_name.setdefault(function.node.name, []).append(function)
        for export_name in _legacy_export_names(sources):
            candidates = by_name.get(export_name, [])
            if len(candidates) == 1:
                names[candidates[0].qualified_name] = "Unknown"
        registry = names

    apis: list[dict[str, Any]] = []
    for qualified_name, lifecycle in sorted(registry.items()):
        function = _resolve_function(qualified_name, functions, verified_exports)
        if function is None:
            apis.append(
                {
                    "qualified_name": qualified_name,
                    "lifecycle": lifecycle,
                    "certainty": "uncertain",
                    "source_path": None,
                    "source_qualified_name": None,
                    "signature": None,
                    "parameters": [],
                    "return_annotation": None,
                    "extraction_error": "Registry entry could not be resolved to one top-level source function.",
                }
            )
            continue
        parameters = _parameters(function.node)
        return_annotation = _annotation(function.node.returns)
        apis.append(
            {
                "qualified_name": qualified_name,
                "lifecycle": lifecycle,
                "certainty": snapshot_certainty,
                "source_path": function.path,
                "source_qualified_name": function.qualified_name,
                "signature": _signature(function.node.name, parameters, return_annotation),
                "parameters": parameters,
                "return_annotation": return_annotation,
                "extraction_error": None,
            }
        )
    if any(record["certainty"] != "certain" for record in apis):
        snapshot_certainty = "uncertain"
        notes.append(
            "One or more registry entries could not be resolved to source; comparison results require review."
        )
    return {
        "version": version,
        "revision": revision,
        "source_kind": source_kind,
        "lifecycle_source": lifecycle_source,
        "certainty": snapshot_certainty,
        "notes": notes,
        "apis": apis,
    }


def _raise_classification(current: str, candidate: str) -> str:
    """Return the more conservative classification."""
    return candidate if CLASSIFICATION_ORDER[candidate] > CLASSIFICATION_ORDER[current] else current


def _parameter_changes(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[list[str], str]:
    """Describe signature changes and classify their compatibility risk."""
    reasons: list[str] = []
    classification = "nonbreaking"
    old_parameters = {parameter["name"]: parameter for parameter in before["parameters"]}
    new_parameters = {parameter["name"]: parameter for parameter in after["parameters"]}
    old_has_var_positional = any(parameter["kind"] == "var_positional" for parameter in before["parameters"])
    old_has_var_keyword = any(parameter["kind"] == "var_keyword" for parameter in before["parameters"])
    for name in sorted(old_parameters.keys() - new_parameters.keys()):
        reasons.append(f"Parameter removed: {name}.")
        classification = "potentially_breaking"
    for name in sorted(new_parameters.keys() - old_parameters.keys()):
        parameter = new_parameters[name]
        if parameter["required"]:
            reasons.append(f"Required parameter added: {name}.")
            classification = "potentially_breaking"
        else:
            old_positional_names = [
                item["name"]
                for item in before["parameters"]
                if item["kind"] in {"positional_only", "positional_or_keyword"}
            ]
            new_positional_names = [
                item["name"]
                for item in after["parameters"]
                if item["kind"] in {"positional_only", "positional_or_keyword"}
            ]
            added_index = new_positional_names.index(name) if name in new_positional_names else -1
            shifts_existing_position = added_index >= 0 and any(
                existing in old_positional_names for existing in new_positional_names[added_index + 1 :]
            )
            if shifts_existing_position:
                reasons.append(f"Optional positional parameter inserted before an existing parameter: {name}.")
                classification = "potentially_breaking"
            elif old_has_var_positional and parameter["kind"] in {"positional_only", "positional_or_keyword"}:
                reasons.append(f"Optional positional parameter can consume an existing *args value: {name}.")
                classification = "potentially_breaking"
            elif old_has_var_keyword and parameter["kind"] in {"positional_or_keyword", "keyword_only"}:
                reasons.append(f"Optional parameter can consume an existing **kwargs key: {name}.")
                classification = "potentially_breaking"
            else:
                reasons.append(f"Optional parameter added: {name}.")
    common = old_parameters.keys() & new_parameters.keys()
    for name in sorted(common):
        old = old_parameters[name]
        new = new_parameters[name]
        if old["kind"] != new["kind"]:
            reasons.append(f"Parameter kind changed for {name}: {old['kind']} to {new['kind']}.")
            classification = "potentially_breaking"
        if old["required"] != new["required"]:
            if new["required"]:
                reasons.append(f"Parameter became required: {name}.")
                classification = "potentially_breaking"
            else:
                reasons.append(f"Parameter became optional: {name}.")
        elif old["has_default"] and new["has_default"] and old["default"] != new["default"]:
            reasons.append(f"Default changed for {name}: {old['default']} to {new['default']}.")
            classification = _raise_classification(classification, "review_required")
        if old["annotation"] != new["annotation"]:
            reasons.append(f"Annotation changed for {name}: {old['annotation']} to {new['annotation']}.")
            classification = _raise_classification(classification, "review_required")
    positional_kinds = {"positional_only", "positional_or_keyword"}
    old_order = [parameter["name"] for parameter in before["parameters"] if parameter["kind"] in positional_kinds]
    new_order = [parameter["name"] for parameter in after["parameters"] if parameter["kind"] in positional_kinds]
    common_order = [name for name in old_order if name in common]
    if common_order != [name for name in new_order if name in common]:
        reasons.append("Existing positional parameter order changed.")
        classification = "potentially_breaking"
    if before["return_annotation"] != after["return_annotation"]:
        reasons.append(
            f"Return annotation changed: {before['return_annotation']} to {after['return_annotation']}."
        )
        classification = _raise_classification(classification, "review_required")
    return reasons, classification


def compare_snapshots(baseline: Mapping[str, Any], target: Mapping[str, Any]) -> dict[str, Any]:
    """Compare two snapshots using conservative public-contract rules."""
    old_apis = {record["qualified_name"]: record for record in baseline["apis"]}
    new_apis = {record["qualified_name"]: record for record in target["apis"]}
    changes: list[dict[str, Any]] = []
    for qualified_name in sorted(old_apis.keys() | new_apis.keys()):
        before = old_apis.get(qualified_name)
        after = new_apis.get(qualified_name)
        if before == after:
            continue
        reasons: list[str] = []
        if before is None:
            change_type = "added"
            classification = "nonbreaking"
            reasons.append("Public API added.")
        elif after is None:
            change_type = "removed"
            classification = "potentially_breaking" if before["lifecycle"] == "Live" else "review_required"
            reasons.append(f"{before['lifecycle']} public API removed.")
        else:
            change_type = "modified"
            classification = "nonbreaking"
            if before["lifecycle"] != after["lifecycle"]:
                reasons.append(f"Lifecycle changed: {before['lifecycle']} to {after['lifecycle']}.")
                if before["lifecycle"] == "Live" and after["lifecycle"] != "Live":
                    classification = "potentially_breaking"
                elif before["lifecycle"] == "Unknown" or after["lifecycle"] == "Unknown":
                    classification = "review_required"
                elif not (before["lifecycle"] == "Preview" and after["lifecycle"] == "Live"):
                    classification = "review_required"
            parameter_reasons, parameter_classification = _parameter_changes(before, after)
            reasons.extend(parameter_reasons)
            classification = _raise_classification(classification, parameter_classification)
            if not reasons:
                reasons.append("Source identity or extraction evidence changed.")
                classification = "review_required"
        if (
            baseline["certainty"] != "certain"
            or target["certainty"] != "certain"
            or (before is not None and before["certainty"] != "certain")
            or (after is not None and after["certainty"] != "certain")
        ):
            reasons.append("Historical API or lifecycle evidence is uncertain; compatibility cannot be established.")
            classification = _raise_classification(classification, "review_required")
        changes.append(
            {
                "qualified_name": qualified_name,
                "change_type": change_type,
                "classification": classification,
                "lifecycle_before": before["lifecycle"] if before else None,
                "lifecycle_after": after["lifecycle"] if after else None,
                "signature_before": before["signature"] if before else None,
                "signature_after": after["signature"] if after else None,
                "reasons": reasons,
            }
        )
    summary = {
        "total": len(changes),
        "added": sum(change["change_type"] == "added" for change in changes),
        "removed": sum(change["change_type"] == "removed" for change in changes),
        "modified": sum(change["change_type"] == "modified" for change in changes),
        "potentially_breaking": sum(
            change["classification"] == "potentially_breaking" for change in changes
        ),
        "nonbreaking": sum(change["classification"] == "nonbreaking" for change in changes),
        "review_required": sum(change["classification"] == "review_required" for change in changes),
    }
    return {
        "baseline": baseline["version"],
        "target": target["version"],
        "summary": summary,
        "changes": changes,
    }


def _release_tags() -> tuple[str, ...]:
    """Return published semantic-version tags in ascending order."""
    tags = [tag for tag in _run_git("tag", "--list").splitlines() if RELEASE_TAG.fullmatch(tag)]
    return tuple(sorted(tags, key=lambda tag: tuple(int(value) for value in tag[1:].split("."))))


def _sources_from_git(ref: str) -> dict[str, str]:
    """Read Python package sources from an exact Git revision."""
    paths = [
        path
        for path in _run_git("ls-tree", "-r", "--name-only", ref, PACKAGE_ROOT).splitlines()
        if path.endswith(".py")
    ]
    return {path: _run_git("show", f"{ref}:{path}") for path in paths}


def _working_tree_sources() -> dict[str, str]:
    """Read current package sources without importing the package."""
    package_dir = ROOT / PACKAGE_ROOT
    return {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(package_dir.rglob("*.py"))
    }


def _source_digest(sources: Mapping[str, str]) -> str:
    """Return a deterministic digest for an exact source mapping."""
    digest = hashlib.sha256()
    for path, text in sorted(sources.items()):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(text.encode("utf-8"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def build_payload(tags: Iterable[str] | None = None) -> dict[str, Any]:
    """Build snapshots and all independently selectable comparisons."""
    selected_tags = tuple(tags) if tags is not None else _release_tags()
    snapshots: list[dict[str, Any]] = []
    for tag in selected_tags:
        revision = _run_git("rev-parse", f"{tag}^{{commit}}").strip()
        snapshots.append(
            build_snapshot(
                version=tag,
                revision=revision,
                source_kind="git_tag",
                sources=_sources_from_git(tag),
            )
        )
    try:
        _run_git("rev-parse", "origin/main^{commit}")
        main_ref = "origin/main"
    except subprocess.CalledProcessError:
        main_ref = "main"
    main_revision = _run_git("rev-parse", f"{main_ref}^{{commit}}").strip()
    main_sources = _sources_from_git(main_ref)
    snapshots.append(
        build_snapshot(
            version="main",
            revision=main_revision,
            source_kind="git_branch",
            sources=main_sources,
        )
    )
    working_tree_sources = _working_tree_sources()
    working_tree_snapshot = build_snapshot(
        version="working-tree",
        revision=None,
        source_kind="working_tree",
        sources=working_tree_sources,
    )
    working_tree_snapshot["source_digest"] = _source_digest(working_tree_sources)
    working_tree_snapshot["notes"].append(
        "This logical target represents the package working tree used for generation. It does not assert a Git branch "
        "identity; source_digest identifies its exact source content."
    )
    snapshots.append(working_tree_snapshot)
    comparisons = [compare_snapshots(baseline, target) for baseline, target in itertools.permutations(snapshots, 2)]
    return {
        "metadata": {
            "schema": SCHEMA,
            "schema_version": 1,
            "authoritative_registry": "src/fabricops_kit/public_api.py",
            "signature_extraction": "Python AST; package modules are not imported.",
            "main_extraction": "The main snapshot uses origin/main when available, otherwise the local main ref; the exact Git commit is recorded.",
            "historical_extraction": "Each tag is read from its own Git tree. Missing registries use uncertain package exports.",
            "working_tree_extraction": (
                "The working-tree target has no Git revision or branch identity; source_digest identifies its content."
            ),
        },
        "versions": [snapshot["version"] for snapshot in snapshots],
        "snapshots": snapshots,
        "comparisons": comparisons,
    }


def write_payload(output_path: Path = OUTPUT_PATH, tags: Iterable[str] | None = None) -> dict[str, Any]:
    """Write the deterministic compatibility payload."""
    payload = build_payload(tags)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if output_path == OUTPUT_PATH:
        update_generated_artifact_metadata(
            artifact_key="public_api_compatibility_json",
            label="Public API compatibility snapshots",
            generator="scripts/generate_public_api_compatibility.py",
            output_path="docs/reference/_data/public-api-compatibility.json",
        )
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    """Generate the committed compatibility contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--tag", action="append", dest="tags", help="Limit generation to one or more tags.")
    args = parser.parse_args(argv)
    write_payload(args.output, args.tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
