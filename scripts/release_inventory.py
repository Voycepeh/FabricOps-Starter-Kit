"""Release inventory discovery, synchronization, and rendering helpers."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib
import json
import inspect
import re
import shutil
import tomllib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"live", "preview", "discontinued"}
GROUPS = ("functions", "metadata_tables", "templates", "dq_rules")
GENERATED_NOTICE_TEMPLATE = "<!-- Generated file. Edit docs/releases/manifests/{version}.yml or the authoritative source metadata and regenerate. -->"
MAINTAINER_FIELDS = {"status", "live_since", "schema_since", "notes", "rationale", "introduced_in", "discontinued_in", "description", "purpose", "managed_by"}
TOP_LEVEL_FIELDS = ("release_version", "release_status", "release_date", "github_owner", "github_repo", "release_motivation", "notebook_pack_asset")
TEMPLATE_DOCS = {
    "00_env_config": "docs/notebook-templates-implementation-guide/environment-config.md",
    "01_agreement": "docs/notebook-templates-implementation-guide/agreement-setup.md",
    "02_pipeline": "docs/notebook-templates-implementation-guide/pipeline-execution.md",
    "03_governance": "docs/notebook-templates-implementation-guide/governance-review.md",
}
GROUP_LABELS = {"functions": "Functions", "metadata_tables": "Metadata tables", "templates": "Notebook templates", "dq_rules": "DQ rules"}
CATEGORY_DIRS = {"functions": "functions", "metadata_tables": "metadata", "templates": "templates", "dq_rules": "dq-rules"}
CATEGORY_NOUN = {"functions": "Function", "metadata_tables": "Table", "templates": "Template", "dq_rules": "DQ rule"}
CATEGORY_PURPOSE = {"functions": "Description", "metadata_tables": "Purpose", "templates": "Purpose", "dq_rules": "Purpose"}


@dataclass(frozen=True)
class ReleaseAsset:
    """Generated release inventory asset fields."""

    name: str
    source_path: str
    documentation_path: str | None = None
    qualified_name: str | None = None
    generated_fields: dict[str, Any] = field(default_factory=dict)

    def as_manifest_item(self) -> dict[str, Any]:
        """Return the generated manifest representation for the asset."""
        item: dict[str, Any] = {"name": self.name}
        if self.qualified_name:
            item["qualified_name"] = self.qualified_name
        item["source_path"] = self.source_path
        if self.documentation_path:
            item["documentation_path"] = self.documentation_path
        item.update(self.generated_fields)
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


def _page_name(name: str) -> str:
    return name.lower() + ".md"


def discover_functions() -> list[ReleaseAsset]:
    """Discover release-facing functions from SUPPORTED_PUBLIC_API."""
    from fabricops_kit.public_api import SUPPORTED_PUBLIC_API

    assets = []
    for qualified_name in SUPPORTED_PUBLIC_API:
        module_name, function_name = qualified_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        source_path = _relative(Path(inspect.getsourcefile(function) or ""))
        assets.append(ReleaseAsset(function_name, source_path, f"docs/api/reference/{function_name}.md", qualified_name))
    return sorted(assets, key=lambda asset: asset.name)


def metadata_schema_fingerprint(schema: Any) -> str:
    """Return a stable SHA-256 fingerprint for a metadata table schema."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_rows

    rows = metadata_table_schema_rows(schema)
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def discover_metadata_tables() -> list[ReleaseAsset]:
    """Discover metadata tables from the canonical metadata schema registry."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    source_path = "src/fabricops_kit/config/metadata_schemas.py"
    registry = metadata_table_schema_registry()
    return [
        ReleaseAsset(
            name,
            source_path,
            f"docs/reference/metadata/{name.lower()}.md",
            generated_fields={"schema_fingerprint": metadata_schema_fingerprint(registry[name])},
        )
        for name in sorted(registry)
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
    return {"functions": discover_functions(), "metadata_tables": discover_metadata_tables(), "templates": discover_templates(), "dq_rules": discover_dq_rules()}


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


def load_release_manifests(manifests_dir: Path = ROOT / "docs" / "releases" / "manifests") -> list[dict[str, Any]]:
    """Load release manifests in deterministic version order."""
    manifests = [manifest for path in sorted(manifests_dir.glob("*.yml")) if (manifest := _load_manifest(path)) is not None]
    return sorted(manifests, key=lambda manifest: Version(str(manifest.get("release_version", "0"))))


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
    for key in TOP_LEVEL_FIELDS:
        if key != "release_version" and existing and key in existing:
            output[key] = existing[key]
    for group, assets in discovered.items():
        existing_by_name = {item["name"]: item for item in (existing or {}).get(group, [])}
        discovered_names = {asset.name for asset in assets}
        missing = [name for name, item in existing_by_name.items() if name not in discovered_names and item.get("status") != "discontinued"]
        if missing:
            raise ValueError(f"Previously tracked {group} asset(s) are no longer discovered: {', '.join(sorted(missing))}. Mark each removed asset as status: discontinued explicitly before regenerating.")
        rows = []
        for asset in assets:
            item = asset.as_manifest_item()
            previous = existing_by_name.get(asset.name, {})
            for key, value in previous.items():
                if key not in item and key in MAINTAINER_FIELDS:
                    item[key] = value
            item["status"] = previous.get("status", "preview")
            if item["status"] == "live":
                item["live_since"] = previous.get("live_since") or previous.get("introduced_in") or version
            if group == "metadata_tables" and item.get("schema_fingerprint"):
                if previous.get("schema_fingerprint") == item["schema_fingerprint"]:
                    item["schema_since"] = previous.get("schema_since") or version
                else:
                    item["schema_since"] = version
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
    for key in TOP_LEVEL_FIELDS:
        if key != "release_version" and key in manifest:
            lines.append(f"{key}: {_format_scalar(manifest[key])}")
    for group in GROUPS:
        lines.append(f"{group}:")
        for item in manifest[group]:
            keys = ["name", "qualified_name", "source_path", "documentation_path", "status", "live_since", "schema_since", "schema_fingerprint"]
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
    manifest = synchronize_manifest(_load_manifest(path), discover_inventory(), version)
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
    pattern = re.compile(rf"^## \[?(?:v)?{re.escape(version)}\]?.*?$\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match or not match.group("body").strip():
        raise ValueError(f"CHANGELOG.md has no release section for {version}")
    return match.group("body").strip()


def project_distribution_names(version: str) -> tuple[str, str]:
    """Return deterministic wheel and source distribution filenames for the project."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["name"]
    wheel_name = project.replace("-", "_")
    return (f"{wheel_name}-{version}-py3-none-any.whl", f"{wheel_name}-{version}.tar.gz")


def release_status_chip(status: str) -> str:
    """Return the rendered release lifecycle status chip for a manifest status."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid lifecycle status: {status!r}.")
    return f'<span class="fabricops-release-status fabricops-release-status--{status}">{status.replace("_", " ").title()}</span>'


def sort_release_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return release manifest items in deterministic status and name order."""
    return sorted(items, key=lambda item: ({"live": 0, "preview": 1, "discontinued": 2}[item["status"]], item["name"]))


def live_release_items(manifest: dict[str, Any], group: str) -> list[dict[str, Any]]:
    """Return deterministic Live items for a manifest group."""
    return [item for item in sort_release_items(manifest[group]) if item["status"] == "live"]


def _function_details(item: dict[str, Any]) -> dict[str, Any]:
    module_name, function_name = item["qualified_name"].rsplit(".", 1)
    function = getattr(importlib.import_module(module_name), function_name)
    doc = inspect.getdoc(function) or ""
    short = doc.splitlines()[0] if doc else item["name"]
    return {"signature": f"{item['name']}{inspect.signature(function)}", "description": short, "doc": doc}


def _function_sections(doc: str) -> tuple[str, str, str]:
    def section(name: str) -> str:
        match = re.search(rf"^{name}\n-+\n(?P<body>.*?)(?=^[A-Z][A-Za-z ]*\n-+\n|\Z)", doc, re.MULTILINE | re.DOTALL)
        return match.group("body").strip() if match else "Not documented in the source docstring."
    return section("Parameters"), section("Returns"), section("Notes")


def _metadata_type(field: Any) -> str:
    from fabricops_kit.config.metadata_schemas import metadata_schema_type_name
    return metadata_schema_type_name(getattr(field, "dataType", ""))


def _metadata_rows(table_name: str) -> list[dict[str, Any]]:
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    schema = metadata_table_schema_registry()[table_name]
    return [{"name": str(f.name), "type": _metadata_type(f), "nullable": "Yes" if bool(getattr(f, "nullable", True)) else "No"} for f in getattr(schema, "fields", [])]


def _template_summary(item: dict[str, Any]) -> dict[str, Any]:
    import json
    data = json.loads((ROOT / item["source_path"]).read_text(encoding="utf-8"))
    markdown = ["".join(c.get("source", [])) for c in data.get("cells", []) if c.get("cell_type") == "markdown"]
    title = markdown[0].strip().splitlines()[0].lstrip("# ") if markdown else item["name"]
    purpose = " ".join(line.strip() for line in (markdown[0].splitlines()[1:4] if markdown else []) if line.strip()) or title
    headings = [line.lstrip("# ").strip().replace("`", "") for block in markdown for line in block.splitlines() if line.startswith("## ")]
    return {"title": title, "purpose": purpose, "flow": headings[:6] or ["Open the notebook in Microsoft Fabric.", "Run cells in order."]}


def _description(item: dict[str, Any], group: str) -> str:
    if item.get("description"):
        return str(item["description"])
    if item.get("purpose"):
        return str(item["purpose"])
    if group == "functions":
        return _function_details(item)["description"].rstrip(".") + "."
    if group == "metadata_tables":
        return f"Supported FabricOps metadata table for {item['name'].removeprefix('METADATA_').lower().replace('_', ' ')}."
    if group == "templates":
        return _template_summary(item)["purpose"]
    return item["name"]


def _category_index(version: str, group: str, items: list[dict[str, Any]], notice: str) -> str:
    lines = [notice, "", f"# FabricOps Starter Kit {version} {GROUP_LABELS[group].lower()}", "", f"Package version: `{version}`", "", f"Live assets in this section: **{len(items)}**.", "", "This frozen release section includes only assets classified as Live for this version.", "", '<div class="fabricops-release-table" markdown>', "", f"| Status | {CATEGORY_NOUN[group]} | {CATEGORY_PURPOSE[group]} | Details |", "| --- | --- | --- | --- |"]
    for item in items:
        lines.append(f"| {release_status_chip('live')} | `{item['name']}` | {_description(item, group)} | [Open]({_page_name(item['name'])}) |")
    lines.extend(["", "</div>", "", "!!! info \"Current product documentation\"", "    Current documentation may include newer Live and Preview capabilities. Use these release pages for the frozen 0.1.0 release surface."])
    return "\n".join(lines) + "\n"


def _function_page(version: str, item: dict[str, Any], notice: str) -> str:
    details = _function_details(item)
    params, returns, notes = _function_sections(details["doc"])
    return f"""{notice}

# `{item['name']}`

{release_status_chip('live')}

Package version: `{version}`

Qualified callable: `{item['qualified_name']}`

Source path: `{item['source_path']}`

Signature: `{details['signature']}`

## Description

{details['description']}

## Parameters

{params}

## Return value

{returns}

## Usage notes

{notes}

[Back to 0.1.0 functions](index.md)
"""


def _metadata_page(version: str, item: dict[str, Any], notice: str) -> str:
    rows = _metadata_rows(item["name"])
    lines = [notice, "", f"# `{item['name']}`", "", release_status_chip("live"), "", f"Package version: `{version}`", "", f"Live since: `{item.get('live_since', version)}`", "", f"Schema since: `{item.get('schema_since', version)}`", "", f"Schema fingerprint: `{item.get('schema_fingerprint', 'Not recorded')}`", "", f"Source path: `{item['source_path']}`", "", "Managed by: `fabricops_kit.config.metadata_schemas.metadata_table_schema_registry`", "", f"Description: {_description(item, 'metadata_tables')}", "", "## Schema", "", "| Column name | Data type | Nullable | Managed by | Description |", "| --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(f"| `{row['name']}` | `{row['type']}` | {row['nullable']} | FabricOps metadata schema registry | `{row['name']}` field in `{item['name']}`. |")
    lines.extend(["", "[Back to 0.1.0 metadata tables](index.md)"])
    return "\n".join(lines) + "\n"


def _template_page(version: str, item: dict[str, Any], notice: str, notebook_pack_url: str) -> str:
    summary = _template_summary(item)
    flow = "\n".join(f"{idx}. {step}" for idx, step in enumerate(summary["flow"], 1))
    source = item["source_path"]
    return f"""{notice}

# `{item['name']}`

{release_status_chip('live')}

Package version: `{version}`

Source notebook path: `{source}`

## Purpose

{summary['purpose']}

## Expected inputs

- Microsoft Fabric notebook runtime with FabricOps Starter Kit {version} installed.
- Any variables or metadata produced by earlier notebooks in the supported release flow.

## Expected outputs

- Notebook state and metadata updates described by the template purpose.
- Release-supported workflow artifacts for downstream notebooks when applicable.

## Short usage flow

{flow}

## Download

[Download the released notebook pack]({notebook_pack_url})

[Back to 0.1.0 notebook templates](index.md)
"""


def _release_url(manifest: dict[str, Any], version: str, asset: str = "") -> str:
    owner = manifest.get("github_owner") or "Voycepeh"
    repo = manifest.get("github_repo") or "FabricOps-Starter-Kit"
    suffix = f"/download/v{version}/{asset}" if asset else f"/tag/v{version}"
    return f"https://github.com/{owner}/{repo}/releases{suffix}"


def render_release_pages() -> list[Path]:
    """Render frozen Live release documentation pages from the current manifest."""
    version = read_package_version()
    path = manifest_path(version)
    manifest = _load_manifest(path)
    if manifest is None:
        raise SystemExit(f"Release manifest not found: {path}. Run scripts/generate_release_inventory.py first.")
    _validate_manifest(manifest, version)
    try:
        notes = extract_changelog_notes(version)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    release_dir = ROOT / "docs" / "releases" / version
    if release_dir.exists():
        for child in release_dir.iterdir():
            if child.is_dir() or child.suffix == ".md":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    release_dir.mkdir(parents=True, exist_ok=True)
    notice = GENERATED_NOTICE_TEMPLATE.format(version=version)
    live = {group: live_release_items(manifest, group) for group in GROUPS}
    wheel, sdist = project_distribution_names(version)
    notebook_pack = manifest.get("notebook_pack_asset") or f"fabricops-kit-{version}-notebooks.zip"
    release_status = manifest.get("release_status") or "Live"
    release_date = manifest.get("release_date") or "Not specified"
    motivation = manifest.get("release_motivation") or "FabricOps 0.1.0 establishes the first supported foundation for governed Microsoft Fabric notebook projects. It focuses on reliable Fabric input and output, dataframe profiling, agreement-driven metadata, and lightweight exploration workflows."

    paths: list[Path] = []
    cards = []
    for group in ("functions", "metadata_tables", "templates", "dq_rules"):
        if live[group]:
            label = GROUP_LABELS[group]
            cards.append(f'<a class="fabricops-release-card" href="{CATEGORY_DIRS[group]}/"><strong>{len(live[group])}</strong><span>Live {label.lower()}</span></a>')
    index = release_dir / "index.md"
    index.write_text("\n".join([notice, "", f"# FabricOps Starter Kit {version}", "", f"- Package version: `{version}`", f"- Release status: {release_status_chip(str(release_status).lower()) if str(release_status).lower() in VALID_STATUSES else release_status}", f"- Release date: {release_date}", f"- [GitHub Release]({_release_url(manifest, version)})", "", "## Why this release exists", "", motivation, "", "## Live in this release", "", '<div class="fabricops-release-card-grid">', *cards, "</div>", "", "## Downloads", "", f"- [Download wheel]({_release_url(manifest, version, wheel)})", f"- [Download source distribution]({_release_url(manifest, version, sdist)})", f"- [Download notebook pack]({_release_url(manifest, version, notebook_pack)})", f"- [View GitHub Release]({_release_url(manifest, version)})", f"- Verify downloads with [SHA256SUMS]({_release_url(manifest, version, 'SHA256SUMS.txt')})", "", "## Get started", "", "1. Download and install the wheel.", "2. Download the released notebook pack.", "3. Run `00_env_config`.", "4. Run `01_agreement`.", "5. Use `99_explore` for supported exploration.", "", "## Known limitations", "", "The pipeline execution workflow, governance review workflow, DQ rule authoring and enforcement, and notebook registry remain Preview and are not part of the supported frozen release surface for 0.1.0.", "", "## Release notes", "", notes, ""]) , encoding="utf-8")
    paths.append(index)

    for group in GROUPS:
        items = live[group]
        if not items:
            continue
        group_dir = release_dir / CATEGORY_DIRS[group]
        group_dir.mkdir(parents=True, exist_ok=True)
        idx = group_dir / "index.md"
        idx.write_text(_category_index(version, group, items, notice), encoding="utf-8")
        paths.append(idx)
        for item in items:
            page = group_dir / _page_name(item["name"])
            if group == "functions":
                content = _function_page(version, item, notice)
            elif group == "metadata_tables":
                content = _metadata_page(version, item, notice)
            elif group == "templates":
                content = _template_page(version, item, notice, _release_url(manifest, version, notebook_pack))
            else:
                content = ""
            page.write_text(content, encoding="utf-8")
            paths.append(page)

    releases_index = ROOT / "docs" / "releases" / "index.md"
    releases_index.write_text(f"{notice}\n\n# Releases\n\n## Current release\n\n- [FabricOps Starter Kit {version}]({version}/)\n", encoding="utf-8")
    return [releases_index, *paths]



def build_notebook_pack(version: str | None = None, output_dir: Path | None = None) -> Path:
    """Build a release notebook ZIP from Live template manifest entries."""
    release_version = version or read_package_version()
    manifest = _load_manifest(manifest_path(release_version))
    if manifest is None:
        raise ValueError(f"Release manifest not found for {release_version}.")
    _validate_manifest(manifest, release_version)
    output_root = output_dir or ROOT / "dist"
    output_root.mkdir(parents=True, exist_ok=True)
    asset_name = manifest.get("notebook_pack_asset") or f"fabricops-kit-{release_version}-notebooks.zip"
    output_path = output_root / str(asset_name)
    live_templates = live_release_items(manifest, "templates")
    if not live_templates:
        raise ValueError(f"Release manifest {release_version} has no Live notebook templates to package.")
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in live_templates:
            source_path = ROOT / str(item["source_path"])
            if not source_path.exists():
                raise ValueError(f"Live notebook template not found: {item['source_path']}")
            info = zipfile.ZipInfo(source_path.name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source_path.read_bytes())
    return output_path

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
