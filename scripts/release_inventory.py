"""Release inventory discovery, synchronization, and rendering helpers."""

from __future__ import annotations

import argparse
import difflib
import importlib
import inspect
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"live", "preview", "discontinued"}
GROUPS = ("functions", "metadata_tables", "templates", "dq_rules")
GENERATED_NOTICE_TEMPLATE = "<!-- Generated file. Edit docs/releases/manifests/{version}.yml and regenerate. -->"
MAINTAINER_FIELDS = {"status", "notes", "rationale", "introduced_in", "discontinued_in"}
TEMPLATE_DOCS = {
    "00_env_config": "docs/notebook-templates-implementation-guide/environment-config.md",
    "01_agreement": "docs/notebook-templates-implementation-guide/agreement-setup.md",
    "02_pipeline": "docs/notebook-templates-implementation-guide/pipeline-execution.md",
    "03_governance": "docs/notebook-templates-implementation-guide/governance-review.md",
}


@dataclass(frozen=True)
class ReleaseAsset:
    """Generated release inventory asset fields."""

    name: str
    source_path: str
    documentation_path: str | None = None
    qualified_name: str | None = None

    def as_manifest_item(self) -> dict[str, Any]:
        """Return the generated manifest representation for the asset."""
        item: dict[str, Any] = {"name": self.name}
        if self.qualified_name:
            item["qualified_name"] = self.qualified_name
        item["source_path"] = self.source_path
        if self.documentation_path:
            item["documentation_path"] = self.documentation_path
        return item


def read_package_version(pyproject_path: Path = ROOT / "pyproject.toml") -> str:
    """Read the release version from ``[project].version`` in pyproject.toml."""
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def manifest_path(version: str) -> Path:
    """Return the default manifest path for a package version."""
    return ROOT / "docs" / "releases" / "manifests" / f"{version}.yml"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _slug(name: str) -> str:
    return name.lower().replace("_", "-")


def discover_functions() -> list[ReleaseAsset]:
    """Discover release-facing functions from SUPPORTED_PUBLIC_API."""
    from fabricops_kit.public_api import SUPPORTED_PUBLIC_API

    assets = []
    for qualified_name in SUPPORTED_PUBLIC_API:
        module_name, function_name = qualified_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        source_path = _relative(Path(inspect.getsourcefile(function) or ""))
        documentation_path = f"docs/api/reference/{function_name}.md"
        assets.append(ReleaseAsset(function_name, source_path, documentation_path, qualified_name))
    return sorted(assets, key=lambda asset: asset.name)


def discover_metadata_tables() -> list[ReleaseAsset]:
    """Discover metadata tables from the canonical metadata schema registry."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    source_path = "src/fabricops_kit/config/metadata_schemas.py"
    return [
        ReleaseAsset(name, source_path, f"docs/reference/metadata/{name.lower()}.md")
        for name in sorted(metadata_table_schema_registry())
    ]


def discover_templates() -> list[ReleaseAsset]:
    """Discover notebook templates from repository template files."""
    assets = []
    for path in sorted((ROOT / "templates" / "notebooks").glob("*.ipynb")):
        name = path.stem
        assets.append(ReleaseAsset(name, _relative(path), TEMPLATE_DOCS.get(name, "docs/notebook-templates-implementation-guide/index.md")))
    return assets


def discover_dq_rules() -> list[ReleaseAsset]:
    """Discover DQ rule types from the authoritative guardrail registry."""
    from fabricops_kit.pipeline import guardrails_shared

    source_path = _relative(Path(inspect.getsourcefile(guardrails_shared) or ""))
    return [ReleaseAsset(name, source_path, f"docs/reference/dq-rules/{_slug(name)}.md") for name in sorted(guardrails_shared.DQ_RULE_TYPES)]


def discover_inventory() -> dict[str, list[ReleaseAsset]]:
    """Discover every release inventory asset group."""
    return {
        "functions": discover_functions(),
        "metadata_tables": discover_metadata_tables(),
        "templates": discover_templates(),
        "dq_rules": discover_dq_rules(),
    }


def _parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if value in {"null", "None"}:
        return None
    return value.strip('"')


def _load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    result: dict[str, Any] = {}
    current_group: str | None = None
    current_item: dict[str, Any] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and raw_line.endswith(":"):
            current_group = raw_line[:-1]
            result[current_group] = []
            continue
        if not raw_line.startswith(" ") and ":" in raw_line:
            key, value = raw_line.split(":", 1)
            result[key] = _parse_scalar(value.strip())
            current_group = None
            continue
        if raw_line.startswith("  - "):
            if current_group is None:
                raise ValueError(f"List item outside a group in {path}: {raw_line}")
            current_item = {}
            result[current_group].append(current_item)
            content = raw_line[4:]
            if content:
                key, value = content.split(":", 1)
                current_item[key] = _parse_scalar(value.strip())
            continue
        if raw_line.startswith("    ") and current_item is not None:
            key, value = raw_line.strip().split(":", 1)
            current_item[key] = _parse_scalar(value.strip())
    return result


def _validate_manifest(manifest: dict[str, Any], version: str) -> None:
    if manifest.get("release_version") != version:
        raise ValueError(f"Manifest release_version {manifest.get('release_version')!r} does not match pyproject.toml version {version!r}.")
    for group in GROUPS:
        seen: set[str] = set()
        for item in manifest.get(group, []):
            name = item.get("name")
            if name in seen:
                raise ValueError(f"Duplicate identifier in {group}: {name}")
            seen.add(name)
            status = item.get("status")
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid lifecycle status for {group} {name}: {status!r}. Use live, preview, or discontinued.")


def synchronize_manifest(existing: dict[str, Any] | None, discovered: dict[str, list[ReleaseAsset]], version: str) -> dict[str, Any]:
    """Synchronize discovered generated fields while preserving maintainer-owned fields."""
    if existing is not None:
        _validate_manifest(existing, version)
    output: dict[str, Any] = {"release_version": version}
    for group, assets in discovered.items():
        existing_by_name = {item["name"]: item for item in (existing or {}).get(group, [])}
        discovered_names = {asset.name for asset in assets}
        missing = [name for name, item in existing_by_name.items() if name not in discovered_names and item.get("status") != "discontinued"]
        if missing:
            raise ValueError(
                f"Previously tracked {group} asset(s) are no longer discovered: {', '.join(sorted(missing))}. "
                "Mark each removed asset as status: discontinued explicitly before regenerating."
            )
        rows = []
        for asset in assets:
            item = asset.as_manifest_item()
            previous = existing_by_name.get(asset.name, {})
            for key, value in previous.items():
                if key not in item and key in MAINTAINER_FIELDS:
                    item[key] = value
            item["status"] = previous.get("status", "preview")
            rows.append(item)
        for name, previous in existing_by_name.items():
            if name not in discovered_names and previous.get("status") == "discontinued":
                rows.append(previous)
        output[group] = sorted(rows, key=lambda item: item["name"])
    return output


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    text = str(value)
    if not text or text.startswith((" ", "-", "#")) or ": " in text:
        return '"' + text.replace('"', '\\"') + '"'
    return text


def dump_manifest(manifest: dict[str, Any]) -> str:
    """Serialize a release manifest deterministically."""
    lines = [f"release_version: {_format_scalar(manifest['release_version'])}"]
    for group in GROUPS:
        lines.append(f"{group}:")
        for item in manifest[group]:
            keys = ["name", "qualified_name", "source_path", "documentation_path", "status"]
            keys.extend(key for key in item if key not in keys)
            first = True
            for key in keys:
                if key not in item:
                    continue
                prefix = "  - " if first else "    "
                lines.append(f"{prefix}{key}: {_format_scalar(item[key])}")
                first = False
    return "\n".join(lines) + "\n"


def generate_inventory(check: bool = False) -> Path:
    """Generate or validate the version-specific release inventory manifest."""
    version = read_package_version()
    path = manifest_path(version)
    discovered = discover_inventory()
    existing = _load_manifest(path)
    manifest = synchronize_manifest(existing, discovered, version)
    expected = dump_manifest(manifest)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if check:
        if current != expected:
            diff = "".join(difflib.unified_diff(current.splitlines(True), expected.splitlines(True), fromfile=str(path), tofile="expected"))
            raise SystemExit(f"Release inventory manifest is stale or missing. Regenerate it with PYTHONPATH=src python scripts/generate_release_inventory.py.\n{diff}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")
    return path


def extract_changelog_notes(version: str, changelog_path: Path = ROOT / "CHANGELOG.md") -> str:
    """Extract release notes from the matching CHANGELOG.md version section."""
    text = changelog_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^## \[?{re.escape(version)}\]?.*?$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return "Release notes have not yet been prepared."
    body = match.group("body").strip()
    return body or "Release notes have not yet been prepared."


def project_distribution_names(version: str) -> tuple[str, str]:
    """Return deterministic wheel and source distribution filenames for the project."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["name"]
    wheel_name = project.replace("-", "_")
    return (f"{wheel_name}-{version}-py3-none-any.whl", f"{wheel_name}-{version}.tar.gz")


def release_status_chip(status: str) -> str:
    """Return the rendered release lifecycle status chip for a manifest status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid lifecycle status: {status!r}.")
    label = status.replace("_", " ").title()
    return f'<span class="fabricops-release-status fabricops-release-status--{status}">{label}</span>'


def sort_release_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return release manifest items in deterministic status and name order."""
    status_order = {"live": 0, "preview": 1, "discontinued": 2}
    return sorted(items, key=lambda item: (status_order[item["status"]], item["name"]))


def render_release_pages() -> list[Path]:
    """Render release contract documentation pages from the current manifest."""
    version = read_package_version()
    path = manifest_path(version)
    manifest = _load_manifest(path)
    if manifest is None:
        raise SystemExit(f"Release manifest not found: {path}. Run scripts/generate_release_inventory.py first.")
    _validate_manifest(manifest, version)
    release_dir = ROOT / "docs" / "releases" / version
    release_dir.mkdir(parents=True, exist_ok=True)
    notes = extract_changelog_notes(version)
    wheel, sdist = project_distribution_names(version)
    notice = GENERATED_NOTICE_TEMPLATE.format(version=version)

    def table(group: str) -> str:
        rows = sort_release_items(manifest[group])
        if not rows:
            return "No assets.\n"
        lines = ["| Status | Name | Documentation | Source |", "| --- | --- | --- | --- |"]
        for item in rows:
            doc = item.get("documentation_path")
            doc_link = f"[{doc}](../../{doc.removeprefix('docs/')})" if doc else "Not documented yet"
            source = item.get("source_path", "")
            lines.append(f"| {release_status_chip(item['status'])} | `{item['name']}` | {doc_link} | `{source}` |")
        return "\n".join(lines) + "\n"

    sections = []
    labels = {"functions": "Functions", "metadata_tables": "Metadata tables", "templates": "Templates", "dq_rules": "DQ rules"}
    for group in GROUPS:
        sections.append(f"## {labels[group]}\n\n{table(group)}")

    content = "\n".join([
        notice,
        "",
        f"# FabricOps Starter Kit {version} release contract",
        "",
        f"Package version: `{version}`",
        "",
        "## Release notes",
        "",
        notes,
        "",
        "## Expected distribution filenames",
        "",
        "These filenames are derived from `pyproject.toml`; verify actual files after `uv build`.",
        "",
        f"- `{wheel}`",
        f"- `{sdist}`",
        "",
        *sections,
    ])
    index = release_dir / "index.md"
    index.write_text(content, encoding="utf-8")

    split_pages: list[Path] = []
    split_names = {
        "functions": "functions.md",
        "metadata_tables": "metadata-tables.md",
        "templates": "templates.md",
        "dq_rules": "dq-rules.md",
    }
    for group, filename in split_names.items():
        split_content = "\n".join([
            notice,
            "",
            f"# {labels[group]} release contract for {version}",
            "",
            f"Package version: `{version}`",
            "",
            f"## {labels[group]}",
            "",
            table(group),
        ])
        split_path = release_dir / filename
        split_path.write_text(split_content, encoding="utf-8")
        split_pages.append(split_path)

    releases_index = ROOT / "docs" / "releases" / "index.md"
    releases_index.write_text(f"{notice}\n\n# Releases\n\n## Current release candidate\n\n- [Proposed initial release {version}]({version}/)\n", encoding="utf-8")
    return [releases_index, index, *split_pages]


def inventory_main(argv: list[str] | None = None) -> int:
    """CLI entry point for release inventory generation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = generate_inventory(check=args.check)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Release inventory {'validated' if args.check else 'written'}: {_relative(path)}")
    return 0


def pages_main() -> int:
    """CLI entry point for release contract page rendering."""
    paths = render_release_pages()
    for path in paths:
        print(f"Release contract page written: {_relative(path)}")
    return 0
