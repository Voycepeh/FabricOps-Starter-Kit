#!/usr/bin/env python3
# ruff: noqa: D103
"""Validate the portable FabricOps Metadata PBIP without Power BI Desktop."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from fabricops_kit.config.metadata_schemas import (  # noqa: E402
    CANONICAL_METADATA_TABLES,
    metadata_table_schema_registry,
)


PROJECT = REPO_ROOT / "powerbi" / "FabricOpsMetadata"
REPORT = PROJECT / "FabricOpsMetadata.Report"
MODEL = PROJECT / "FabricOpsMetadata.SemanticModel"
TABLES = MODEL / "definition" / "tables"


class ValidationError(RuntimeError):
    """Raised for one deterministic project validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"Invalid JSON in {path.relative_to(REPO_ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"Expected JSON object in {path.relative_to(REPO_ROOT)}")
    return value


def canonical_columns() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    scalar: dict[str, set[str]] = {}
    complex_fields: dict[str, set[str]] = {}
    for table_name, schema in metadata_table_schema_registry().items():
        scalar[table_name] = set()
        complex_fields[table_name] = set()
        for field in schema.fields:
            if hasattr(field.dataType, "fields") or hasattr(field.dataType, "elementType"):
                complex_fields[table_name].add(field.name)
            else:
                scalar[table_name].add(field.name)
    return scalar, complex_fields


def validate_layout() -> None:
    pbip = load_json(PROJECT / "FabricOpsMetadata.pbip")
    require(pbip.get("version") == "1.0", "PBIP version must be 1.0")
    require(
        pbip.get("artifacts") == [{"report": {"path": "FabricOpsMetadata.Report"}}],
        "PBIP report artifact path is not portable",
    )
    pbir = load_json(REPORT / "definition.pbir")
    require(pbir.get("version") == "4.0", "PBIR definition version must be 4.0")
    require(
        pbir.get("datasetReference", {}).get("byPath", {}).get("path") == "../FabricOpsMetadata.SemanticModel",
        "PBIR semantic model must use a relative byPath reference",
    )
    pbism = load_json(MODEL / "definition.pbism")
    require(pbism.get("version") == "4.2", "Semantic model definition version must be 4.2")
    database = (MODEL / "definition" / "database.tmdl").read_text(encoding="utf-8")
    require("compatibilityLevel: 1702" in database, "Semantic model compatibility level must support current TMDL")


def validate_sources() -> dict[str, set[str]]:
    scalar, complex_fields = canonical_columns()
    model_fields: dict[str, set[str]] = {}
    for table_name in CANONICAL_METADATA_TABLES:
        path = TABLES / f"{table_name}.tmdl"
        require(path.exists(), f"Missing canonical TMDL table: {table_name}")
        text = path.read_text(encoding="utf-8")
        require("\n\t\tmode: import" in text, f"{table_name} is not Import mode")
        match = re.search(
            rf'FabricOpsSqlTable\([^\n]+, "{re.escape(table_name)}", \{{([^}}]*)\}}, (true|false)\)', text
        )
        require(match is not None, f"{table_name} does not use the shared scalar SQL projection")
        projected = set(re.findall(r'"([^"]+)"', match.group(1)))
        require(
            projected == scalar[table_name],
            f"{table_name} scalar projection drift: missing={sorted(scalar[table_name] - projected)}, extra={sorted(projected - scalar[table_name])}",
        )
        require(not projected.intersection(complex_fields[table_name]), f"{table_name} projects native complex columns")
        expected_flag = "true" if complex_fields[table_name] else "false"
        require(match.group(2) == expected_flag, f"{table_name} complex-bearing flag is incorrect")
        declared = set(re.findall(r"^\tcolumn (?:'((?:[^']|'')+)'|([^\n]+))$", text, re.MULTILINE))
        flattened = {quoted.replace("''", "'") if quoted else plain for quoted, plain in declared}
        model_fields[table_name] = flattened

    expressions = (MODEL / "definition" / "expressions.tmdl").read_text(encoding="utf-8")
    for parameter in (
        "pSqlEndpoint",
        "pDatabaseName",
        "pGovernanceSchema",
        "pEngineeringSchema",
        "pLoadComplexBearingTables",
    ):
        require(
            f"expression {parameter} =" in expressions and "IsParameterQuery=true" in expressions,
            f"Missing parameter {parameter}",
        )
    require(
        "Sql.Database(pSqlEndpoint, pDatabaseName" in expressions,
        "Power Query is not parameterized through Sql.Database",
    )
    require("Value.NativeQuery" in expressions and "SELECT " in expressions, "Scalar native SQL projection is missing")
    require("#table(ScalarColumns, {})" in expressions, "Explicit complex-table compatibility projection is missing")
    require(
        "workspace" not in expressions.lower().replace("pgovernanceschema", "").replace("pengineeringschema", "")
        or "workspace_id" not in expressions,
        "Connection expressions appear to hardcode a workspace",
    )
    return model_fields


def tmdl_declared_fields(path: Path) -> set[str]:
    fields = set()
    for quoted, plain in re.findall(
        r"^\tcolumn (?:'((?:[^']|'')+)'|([^\n=]+?))(?:\s*=.*)?$", path.read_text(encoding="utf-8"), re.MULTILINE
    ):
        fields.add((quoted.replace("''", "'") if quoted else plain).strip())
    return fields


def validate_model(model_fields: dict[str, set[str]]) -> None:
    for table_name in ("Date", "DimTable", "DimWorkspace", "DimPipeline", "_Measures"):
        path = TABLES / f"{table_name}.tmdl"
        require(path.exists(), f"Missing semantic table {table_name}")
        model_fields[table_name] = tmdl_declared_fields(path)
    measures_text = (TABLES / "_Measures.tmdl").read_text(encoding="utf-8")
    measures = set(re.findall(r"^\tmeasure (?:'((?:[^']|'')+)'|([^=\n]+?))\s*=", measures_text, re.MULTILINE))
    model_fields["_Measures"] = {(quoted.replace("''", "'") if quoted else plain).strip() for quoted, plain in measures}
    require(len(model_fields["_Measures"]) >= 30, "Expected reusable DAX measure library")

    relationships = (MODEL / "definition" / "relationships.tmdl").read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=relationship )", relationships.strip())
    require(len(blocks) >= 20, "Expected model relationship set")
    pairs = []
    for block in blocks:
        from_match = re.search(r"\tfromColumn: (.+)", block)
        to_match = re.search(r"\ttoColumn: (.+)", block)
        require(from_match is not None and to_match is not None, "Relationship is missing an endpoint")
        pairs.append((from_match.group(1), to_match.group(1)))
    require(len(pairs) == len(set(pairs)), "Duplicate model relationships found")
    require(
        "METADATA_PROCESSING_STATE.target_workspace_table_key" in relationships and "isActive: false" in relationships,
        "Target Processing State relationship must be inactive",
    )
    require(
        "METADATA_DATA_AGREEMENT.recipient_steward_id" in relationships,
        "Recipient Steward role relationship is missing",
    )


def validate_report(model_fields: dict[str, set[str]]) -> None:
    definition = REPORT / "definition"
    load_json(definition / "report.json")
    load_json(definition / "version.json")
    pages_metadata = load_json(definition / "pages" / "pages.json")
    page_order = pages_metadata.get("pageOrder")
    require(isinstance(page_order, list) and len(page_order) == 6, "Report must contain six ordered pages")
    expected_names = [
        "01 — Overview",
        "02 — Data Catalogue",
        "03 — Governance",
        "04 — Data Quality",
        "05 — Pipeline Operations",
        "06 — Lineage & Access",
    ]
    actual_names = []
    total_visuals = 0
    for page_id in page_order:
        page_dir = definition / "pages" / page_id
        page = load_json(page_dir / "page.json")
        require(page.get("name") == page_id, f"Page directory/name mismatch for {page_id}")
        actual_names.append(page.get("displayName"))
        visuals = sorted(page_dir.glob("visuals/*/visual.json"))
        require(len(visuals) >= 14, f"Page {page.get('displayName')} has too few visuals")
        total_visuals += len(visuals)
        for visual_path in visuals:
            visual = load_json(visual_path)
            require(
                visual.get("name") == visual_path.parent.name,
                f"Visual directory/name mismatch: {visual_path.relative_to(REPO_ROOT)}",
            )
            query_state = visual.get("visual", {}).get("query", {}).get("queryState", {})
            for role in query_state.values():
                for projection in role.get("projections", []):
                    field = projection.get("field", {})
                    payload = field.get("Column") or field.get("Measure")
                    require(
                        isinstance(payload, dict),
                        f"Unsupported visual field reference in {visual_path.relative_to(REPO_ROOT)}",
                    )
                    source = payload.get("Expression", {}).get("SourceRef", {}).get("Entity")
                    prop = payload.get("Property")
                    require(source in model_fields, f"Visual references unknown table {source}")
                    require(prop in model_fields[source], f"Visual references unknown field {source}[{prop}]")
    require(actual_names == expected_names, f"Unexpected report page names/order: {actual_names}")
    require(total_visuals >= 100, "Report definition is unexpectedly sparse")


def validate_docs() -> None:
    readme = (PROJECT / "README.md").read_text(encoding="utf-8")
    mapping = (PROJECT / "SOURCE_TO_MODEL.md").read_text(encoding="utf-8")
    for required in (
        "Scheduled refresh",
        "pSqlEndpoint",
        "pLoadComplexBearingTables",
        "ARRAY",
        "STRUCT",
        "signed-in Fabric environment",
    ):
        require(required.lower() in readme.lower(), f"Setup guide is missing {required}")
    for table_name in CANONICAL_METADATA_TABLES:
        require(f"`{table_name}`" in mapping, f"Source mapping is missing {table_name}")
    require("transformation-level lineage" in readme, "Lineage limitation is not documented")
    require("effective access" in readme, "Access observation limitation is not documented")


def main() -> None:
    validate_layout()
    model_fields = validate_sources()
    validate_model(model_fields)
    validate_report(model_fields)
    validate_docs()
    json_count = 0
    for path in PROJECT.rglob("*.json"):
        load_json(path)
        json_count += 1
    print(f"PASS: FabricOps Metadata PBIP ({json_count} JSON files, 12 canonical tables, 6 report pages)")


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
