"""Validate the PBIP links, public JSON schemas and native visual field bindings.

Run with Python 3.11+ and jsonschema. Use --schema-cache to reuse downloaded
Microsoft schemas. This check does not execute Power Query or DAX.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from jsonschema.validators import validator_for
from referencing import Registry, Resource

PROJECT = Path(__file__).resolve().parents[1]
HOST = "developer.microsoft.com"


def read(path):
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def schema_registry(cache):
    """Resolve Microsoft schemas and their transitive references."""
    def retrieve(uri):
        handle = urlparse(uri)
        if handle.scheme != "https" or handle.netloc != HOST or not handle.path.startswith("/json-schemas/"):
            raise ValueError(f"Unexpected schema origin: {uri}")
        path = cache.joinpath(*handle.path.lstrip("/").split("/"))
        if not path.exists():
            with urlopen(uri, timeout=30) as response:
                content = response.read()
            json.loads(content)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return Resource.from_contents(read(path))

    return Registry(retrieve=retrieve), retrieve


def model_fields(model):
    """Read model table, column and measure declarations for binding checks."""
    result = {}
    for table in (model / "definition/tables").glob("*.tmdl"):
        declarations = {"Column": set(), "Measure": set()}
        for match in re.finditer(r"^\t(column|measure) (?:'([^']+)'|([^\s=]+))", table.read_text(), re.M):
            kind, quoted, plain = match.groups()
            declarations[kind.title()].add(quoted or plain)
        result[table.stem] = declarations
    return result


def check_dax_references(model, fields):
    """Check explicit DAX model references and relationship endpoints."""
    all_measures = set().union(*(item["Measure"] for item in fields.values()))
    for path in (model / "definition/tables").glob("*.tmdl"):
        text = path.read_text()
        dax_regions = re.findall(r"^\t(?:measure .* =|\tmode: import\n\t\tsource =)(\n(?:\t{3,}[^\n]*\n)+)", text, re.M)
        for region in dax_regions:
            if region.lstrip().startswith("let"):
                continue
            code = re.sub(r'"(?:""|[^"])*"', '""', region)
            for table, name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\[([^\]]+)\]", code):
                assert table in fields and name in fields[table]["Column"] | fields[table]["Measure"], (path.name, table, name)
            for name in re.findall(r"(?<![\w.'])\[([^\]]+)\]", code):
                assert name in all_measures, (path.name, name)
    relationship_text = (model / "definition/relationships.tmdl").read_text()
    for table, column in re.findall(r"^\t(?:from|to)Column: ([^.]+)\.'([^']+)'$", relationship_text, re.M):
        assert column in fields[table]["Column"], (table, column)


def scan_fields(value, model, aliases=None):
    """Walk semantic query fields with local aliases for filter expressions."""
    if isinstance(value, list):
        for item in value:
            scan_fields(item, model, aliases)
    if not isinstance(value, dict):
        return
    aliases = dict(aliases or {})
    aliases.update({row["Name"]: row["Entity"] for row in value.get("From", []) if "Entity" in row})
    for kind in ("Column", "Measure"):
        binding = value.get(kind)
        if isinstance(binding, dict) and "Property" in binding:
            source = binding.get("Expression", {}).get("SourceRef", {})
            entity = source.get("Entity") or aliases.get(source.get("Source"))
            assert entity, (kind, binding)
            if entity:
                assert binding["Property"] in model[entity][kind], (entity, kind, binding["Property"])
    for child in value.values():
        scan_fields(child, model, aliases)


def main():
    """Run project-level validations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema-cache", type=Path, default=Path("/tmp/fabricops-pbip-schemas"))
    args = parser.parse_args()
    registry, retrieve = schema_registry(args.schema_cache)
    project_file, = PROJECT.glob("*.pbip")
    artifact, = read(project_file)["artifacts"]
    report = PROJECT / artifact["report"]["path"]
    model = (report / read(report / "definition.pbir")["datasetReference"]["byPath"]["path"]).resolve()
    assert model.parent == PROJECT and (model / "definition.pbism").is_file()
    fields = model_fields(model)
    check_dax_references(model, fields)
    docs = [project_file, report / "definition.pbir", model / "definition.pbism", *report.rglob("*.json")]
    validated = 0
    errors = []
    for path in docs:
        value = read(path)
        if "$schema" not in value:
            continue
        try:
            resource = retrieve(value["$schema"])
            Validator = validator_for(resource.contents)
            validator = Validator(resource.contents, registry=registry, _resolver=registry.resolver(value["$schema"]))
            for error in validator.iter_errors(value):
                errors.append(f"{path.relative_to(PROJECT)} {error.json_path}: {error.message}")
            scan_fields(value, fields)
        except Exception as exc:
            errors.append(f"{path.relative_to(PROJECT)}: {exc}")
        validated += 1
    pages_path = report / "definition/pages"
    pages = read(pages_path / "pages.json")
    assert pages["activePageName"] in pages["pageOrder"]
    assert set(pages["pageOrder"]) == {path.parent.name for path in pages_path.glob("*/page.json")}
    bookmarks = report / "definition/bookmarks"
    bookmark_names = {item["name"] for item in read(bookmarks / "bookmarks.json")["items"]}
    assert bookmark_names == {path.name.split(".")[0] for path in bookmarks.glob("*.bookmark.json")}
    visual_count = 0
    for page_dir in (pages_path / name for name in pages["pageOrder"]):
        page = read(page_dir / "page.json")
        assert page["name"] == page_dir.name
        visuals = {path.parent.name: read(path) for path in page_dir.glob("visuals/*/visual.json")}
        for key, visual in visuals.items():
            assert key == visual["name"]
            pos = visual["position"]
            assert pos["x"] >= 0 and pos["y"] >= 0
            assert pos["x"] + pos["width"] <= page["width"] and pos["y"] + pos["height"] <= page["height"]
        for interaction in page.get("visualInteractions", []):
            assert interaction["source"] in visuals and interaction["target"] in visuals
        visual_count += len(visuals)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {validated} JSON definitions, {len(pages['pageOrder'])} pages and {visual_count} visual bindings.")


if __name__ == "__main__":
    main()
