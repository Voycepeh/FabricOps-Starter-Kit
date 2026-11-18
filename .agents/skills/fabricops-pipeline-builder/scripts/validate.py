"""Check the structure and declared configuration of a FabricOps Git notebook."""

import argparse
import ast
import inspect
import json
import re
from importlib.metadata import version
from pathlib import Path
from uuid import UUID

SECTIONS = {
    "Setup": ("setup_notebook", "setup_pipeline"),
    "Read": ("orchestrate_read",),
    "Transform": (),
    "Write": ("orchestrate_write",),
    "Finalize": ("finalize_pipeline",),
}
ENTRY_POINTS = {name for names in SECTIONS.values() for name in names}
TABLE_WRITE_MODES = {"overwrite", "append_all", "append_new_only", "scd1", "scd2"}
PYSPARK = {"language": "python", "language_group": "synapse_pyspark"}
PLATFORM_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json"


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _platform(notebook):
    if notebook.suffix != ".Notebook":
        raise ValueError("Use a <name>.Notebook item directory.")
    platform = json.loads((notebook / ".platform").read_text(encoding="utf-8"))
    metadata, config = platform["metadata"], platform["config"]
    if (platform["$schema"] != PLATFORM_SCHEMA or metadata["type"] != "Notebook"
            or not _text(metadata["displayName"]) or config["version"] != "2.0"):
        raise ValueError("Expected a version 2 Fabric Notebook .platform descriptor.")
    if UUID(config["logicalId"]).int == 0:
        raise ValueError("The Fabric Notebook logicalId must be a nonzero UUID.")
    if any((notebook / name).exists() for name in ("item.metadata.json", "item.config.json")):
        raise ValueError("A version 2 .platform descriptor cannot coexist with version 1 system files.")


def _metadata(body):
    lines = body.strip().splitlines()
    if not lines or any(not line.startswith("# META ") for line in lines):
        raise ValueError("Fabric metadata must use # META lines.")
    return json.loads("\n".join(line.removeprefix("# META ") for line in lines))


def _sections(source):
    header, *parts = re.split(r"^# (MARKDOWN|CELL|METADATA) \*{20}[ \t]*\n", source, flags=re.MULTILINE)
    if header.strip() != "# Fabric notebook source":
        raise ValueError("Missing Fabric notebook source header.")
    blocks = list(zip(parts[::2], parts[1::2]))
    if not blocks or blocks[0][0] != "METADATA":
        raise ValueError("Missing Fabric notebook metadata.")
    if _metadata(blocks[0][1])["kernel_info"]["name"] != "synapse_pyspark":
        raise ValueError("Use the synapse_pyspark kernel.")
    found = {}
    active = None
    last_kind = "METADATA"
    for kind, body in blocks[1:]:
        if last_kind == "CELL" and kind != "METADATA":
            raise ValueError("Each Fabric code cell must have PySpark metadata.")
        if kind == "MARKDOWN":
            lines = body.strip().splitlines()
            if any(not line.startswith("#") and line.strip() for line in lines):
                raise ValueError("Fabric Markdown cells must use commented source.")
            heading = lines[0].removeprefix("# ## ") if lines else ""
            if heading in SECTIONS:
                if heading in found:
                    raise ValueError(f"Duplicate section {heading}.")
                active = heading
                found[active] = []
        elif kind == "CELL":
            if active is None:
                raise ValueError("Place code under a pipeline section heading.")
            compile(body, f"<{active} cell>", "exec")
            found[active].extend(ast.parse(body).body)
        elif last_kind != "CELL" or not PYSPARK.items() <= _metadata(body).items():
            raise ValueError("Expected Python and synapse_pyspark cell metadata.")
        last_kind = kind
    if last_kind == "CELL":
        raise ValueError("Each Fabric code cell must have PySpark metadata.")
    if tuple(found) != tuple(SECTIONS) or not all(found.values()):
        raise ValueError("Expected code in Setup, Read, Transform, Write and Finalize, in that order.")
    return found


def _calls(sections):
    imported = set()
    calls = {name: [] for name in sorted(ENTRY_POINTS)}
    for section, statements in sections.items():
        stage_calls = []
        for statement in statements:
            direct = getattr(statement, "value", None)
            for node in ast.walk(statement):
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "fabricops_kit":
                    if (section != "Setup" or node is not statement or node.level
                            or node.module != "fabricops_kit"
                            or any(name.asname or name.name not in ENTRY_POINTS for name in node.names)):
                        raise ValueError("Import only the pipeline entry points from fabricops_kit in Setup.")
                    imported.update(name.name for name in node.names)
                if isinstance(node, ast.Import) and any(
                    name.name.split(".")[0] == "fabricops_kit" for name in node.names
                ):
                    raise ValueError("Import the FabricOps pipeline entry points by name.")
                if isinstance(node, ast.Attribute) and node.attr in {"write", "writeStream", "writeTo", "saveAsTable", "insertInto"}:
                    raise ValueError("Use orchestrate_write for persistence.")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ENTRY_POINTS:
                    name = node.func.id
                    if node is not direct or name not in SECTIONS[section] or name not in imported:
                        raise ValueError(f"Call imported {name} directly in its pipeline section.")
                    stage_calls.append(name)
                    calls[name].append(node)
                    if name == "setup_pipeline" and (
                        not isinstance(statement, ast.Assign) or len(statement.targets) != 1
                        or not isinstance(statement.targets[0], ast.Name) or statement.targets[0].id != "pipeline"
                    ):
                        raise ValueError("Save the setup_pipeline session as pipeline.")
        expected = SECTIONS[section]
        if section in {"Read", "Write"}:
            if not stage_calls:
                raise ValueError(f"Missing {expected[0]} in {section}.")
        elif tuple(stage_calls) != expected:
            raise ValueError(f"Unexpected lifecycle calls in {section}. Expected {', '.join(expected) or 'none'}.")
    return calls


def _parameters(name, call, package):
    if any(isinstance(item, ast.Starred) for item in call.args) or any(kw.arg is None for kw in call.keywords):
        raise ValueError(f"Use explicit arguments in {name}.")
    keywords = {kw.arg: kw.value for kw in call.keywords}
    signature = inspect.signature(getattr(package, name))
    bound = signature.bind(*call.args, **keywords)
    bound.apply_defaults()
    options = {}
    for key, value in bound.arguments.items():
        if (name, key) == ("orchestrate_write", "dataframe"):
            continue
        if (name, key) == ("finalize_pipeline", "pipeline"):
            if not isinstance(value, ast.Name) or value.id != "pipeline":
                raise ValueError("Pass the pipeline session to finalize_pipeline.")
            continue
        if isinstance(value, ast.AST):
            try:
                value = ast.literal_eval(value)
            except ValueError:
                raise ValueError(f"Use a literal value for {name}.{key}.") from None
        options[key] = value
    return options


def _location(options, stores, *, write):
    store = options["store"]
    if not _text(store) or store not in stores:
        raise ValueError("Use a confirmed store alias supplied with --store.")
    if store.casefold() == "metadata":
        raise ValueError("Use a business store for Read and Write. FabricOps routes its own metadata.")
    path = options.get("relative_path")
    if path is not None:
        if (not _text(path) or path.casefold().startswith("files/") or re.search(r"[:\\{}%]", path)
                or any(part in {"", ".", ".."} for part in path.split("/"))):
            raise ValueError("Use a relative Lakehouse Files path beneath the configured Files root.")
        if write and re.search(r"[?*\[\]]", path):
            raise ValueError("Use an exact path for a file target.")
        if options.get("table_name") is not None or options.get("schema") is not None:
            raise ValueError("Use table or Files coordinates for an operation.")
        formats = ("csv", "json", "parquet") if write else ("csv", "json", "parquet", "excel")
        if options.get("file_format") not in formats:
            raise ValueError(f"Specify a supported file_format ({', '.join(formats)}).")
        return (store.casefold(), "files", path.casefold())
    schema, table = options.get("schema"), options.get("table_name")
    if options.get("file_format") is not None:
        raise ValueError("A file format requires relative_path.")
    if not _text(table) or (schema is not None and not _text(schema)):
        raise ValueError("Provide a table_name and the configured schema, or an explicit schemaless None.")
    if any(re.search(r"[./\\:<>{}]", name) for name in (schema, table) if name is not None):
        raise ValueError("Use unqualified table and schema names as separate arguments.")
    return (store.casefold(), "table", (schema or "").casefold(), table.casefold())


def _overlap(first, second):
    if first[:2] != second[:2]:
        return False
    if first[1] == "table":
        return first[3] == second[3] and (first[2] == second[2] or not first[2] or not second[2])
    left, right = first[2], second[2]
    if re.search(r"[?*\[\]]", right):
        prefix = re.split(r"[?*\[\]]", right, maxsplit=1)[0]
        return left.startswith(prefix) or prefix.startswith(left + "/")
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _configured_location(options, call, stores, *, write):
    location = _location(options, stores, write=write)
    if location[1] == "table" and not any(kw.arg == "schema" for kw in call.keywords):
        raise ValueError("Set schema explicitly, using None for a schemaless store.")
    file_options = options.get("write_options" if write else "read_options")
    if file_options is not None:
        if location[1] != "files" or not isinstance(file_options, dict):
            raise ValueError("File options require a Lakehouse Files operation and a dictionary.")
        if any(not _text(key) or key.casefold() in {"path", "paths", "mode"} for key in file_options):
            raise ValueError("File options cannot override the location or mode.")
    return location


def validate(notebook, stores, expected_version):
    """Validate notebook source against the installed dependency without running any cells."""
    import fabricops_kit

    installed = version("fabricops-kit")
    if installed != expected_version:
        raise ValueError(f"Installed fabricops-kit {installed} differs from expected {expected_version}.")
    _platform(notebook)
    source = (notebook / "notebook-content.py").read_text(encoding="utf-8")
    calls = _calls(_sections(source))
    options = {
        name: [_parameters(name, call, fabricops_kit) for call in stage_calls]
        for name, stage_calls in calls.items()
    }

    setup = options["setup_notebook"][0]
    if any(setup.get(key) is not None for key in ("config", "workspace_id", "config_workspace_id")):
        raise ValueError("Keep physical binding configuration in the approved Fabric deployment.")
    mode = options["setup_pipeline"][0]["pipeline_mode"]
    if mode not in ("Dry Run", "Ungoverned") or not any(
        kw.arg == "pipeline_mode" for kw in calls["setup_pipeline"][0].keywords
    ):
        raise ValueError("Set pipeline_mode explicitly to Dry Run or explicitly reviewed Ungoverned.")
    read_locations = []
    incremental_targets = []
    for read, call in zip(options["orchestrate_read"], calls["orchestrate_read"]):
        read_locations.append(_configured_location(read, call, stores, write=False))
        if not any(kw.arg == "read_mode" for kw in call.keywords) or read["read_mode"] not in ("full", "incremental"):
            raise ValueError("Set read_mode explicitly to full or incremental.")
        if read.get("relative_path") is not None and (
            read["read_mode"] != "full" or any(read.get(key) is not None for key in (
                "query", "read_parameters", "target_store", "target_schema", "target_table_name"
            ))
        ):
            raise ValueError("Files reads use full mode and cannot use SQL or table processing settings.")
        read_parameters = read.get("read_parameters")
        target = {name: read.get(f"target_{name}") for name in ("store", "schema", "table_name")}
        if read["read_mode"] == "incremental":
            if read.get("query") is not None:
                raise ValueError("Incremental Read cannot use caller SQL.")
            if (not isinstance(read_parameters, dict) or read_parameters.keys() != {"watermark_column"}
                    or not _text(read_parameters["watermark_column"])):
                raise ValueError("Incremental Read requires an explicit read_parameters.watermark_column.")
            incremental_targets.append(_location(target, stores, write=True))
        else:
            if read_parameters is not None:
                raise ValueError("Full Read does not accept read_parameters.")
            if any(value is not None for value in target.values()):
                _location(target, stores, write=True)

    writes = {}
    for write, call in zip(options["orchestrate_write"], calls["orchestrate_write"]):
        target = _configured_location(write, call, stores, write=True)
        if any(_overlap(target, location) for location in (*read_locations, *writes)):
            raise ValueError("A target overlaps a declared source or another target.")
        strategy = write["write_mode"]
        modes = ("overwrite", "append_all") if target[1] == "files" else TABLE_WRITE_MODES
        if not _text(strategy) or strategy not in modes:
            raise ValueError("Choose a supported Write strategy for the target.")
        parameters = write.get("write_parameters")
        if parameters is not None and (not isinstance(parameters, dict) or target[1] == "files"):
            raise ValueError("Only table targets accept a write_parameters dictionary.")
        parameters = parameters or {}
        if target[1] == "files" and (
            write.get("existing_mapping") is not None
            or (strategy == "overwrite" and not write["relative_path"].endswith("." + write["file_format"]))
        ):
            raise ValueError("Files writes have no token mapping and Overwrite requires the matching file extension.")
        if strategy in ("scd1", "scd2"):
            keys = parameters.get("key_columns")
            if not isinstance(keys, (list, tuple)) or not keys or not all(map(_text, keys)) or len(set(keys)) != len(keys):
                raise ValueError(f"{strategy} requires nonempty, distinct key_columns.")
        if strategy == "scd2" and not _text(parameters.get("effective_column")):
            raise ValueError("scd2 requires effective_column.")
        writes[target] = strategy

    if incremental_targets and any(
        strategy == "overwrite" or location[1] == "files" for location, strategy in writes.items()
    ):
        raise ValueError("Incremental Read cannot feed whole-table Overwrite or a Files Write.")
    for target in incremental_targets:
        if target not in writes:
            raise ValueError("Incremental Read target coordinates must match a table Write.")
    return f"FabricOps {installed} | {mode} | {len(read_locations)} Read(s), {len(writes)} Write(s)"


def main():
    """Run portable, local validation and return a shell exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--store", action="append", required=True, help="Confirmed configured alias. Repeat per store.")
    parser.add_argument("--fabricops-version", required=True, help="FabricOps version pinned for the consumer.")
    args = parser.parse_args()
    try:
        report = validate(args.notebook, args.store, args.fabricops_version)
    except (AttributeError, ImportError, KeyError, OSError, SyntaxError, TypeError, ValueError) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    print(f"Local validation passed | {report}")
    print("Fabric Git sync, physical bindings, data, permissions and execution require Fabric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
