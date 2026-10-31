#!/usr/bin/env python3
# ruff: noqa: D103
"""Generate the source-controlled FabricOps Metadata Power BI project.

The canonical metadata schema remains owned by metadata_schemas.py.  This
generator imports that registry, projects only SQL-endpoint-compatible scalar
columns, and emits a PBIP/PBIR/TMDL project without changing source metadata.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from fabricops_kit.config.metadata_schemas import (  # noqa: E402
    CANONICAL_METADATA_TABLES,
    metadata_schema_type_name,
    metadata_table_owner,
    metadata_table_schema_registry,
)


PROJECT_ROOT = REPO_ROOT / "powerbi" / "FabricOpsMetadata"
REPORT_ROOT = PROJECT_ROOT / "FabricOpsMetadata.Report"
MODEL_ROOT = PROJECT_ROOT / "FabricOpsMetadata.SemanticModel"
DEFINITION_ROOT = REPORT_ROOT / "definition"
PAGES_ROOT = DEFINITION_ROOT / "pages"
TABLES_ROOT = MODEL_ROOT / "definition" / "tables"

SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
COLORS = {
    "navy": "#172554",
    "blue": "#2563EB",
    "blue_light": "#DBEAFE",
    "purple": "#7C3AED",
    "purple_light": "#EDE9FE",
    "ink": "#172033",
    "muted": "#64748B",
    "canvas": "#F5F7FB",
    "white": "#FFFFFF",
    "green": "#059669",
    "amber": "#D97706",
    "red": "#DC2626",
}

TYPE_MAP = {
    "string": ("string", "type text"),
    "boolean": ("boolean", "type logical"),
    "long": ("int64", "Int64.Type"),
    "integer": ("int64", "Int64.Type"),
    "double": ("double", "type number"),
    "date": ("dateTime", "type date"),
    "timestamp": ("dateTime", "type datetime"),
}

KEY_COLUMNS = {
    "METADATA_DATA_AGREEMENT": [("agreement_key", "string")],
    "METADATA_DATA_CONTRACT": [("contract_key", "string"), ("contract_committed_date", "date")],
    "METADATA_DATA_CATALOGUE": [
        ("workspace_table_key", "string"),
        ("workspace_column_key", "string"),
        ("catalogue_committed_date", "date"),
    ],
    "METADATA_DATA_PROFILED": [
        ("workspace_table_key", "string"),
        ("workspace_column_key", "string"),
        ("profile_date", "date"),
    ],
    "METADATA_DATA_PROFILED_FREQUENCY": [
        ("workspace_table_key", "string"),
        ("workspace_column_key", "string"),
        ("frequency_profile_date", "date"),
    ],
    "METADATA_DATA_LINEAGE": [("workspace_table_key", "string"), ("lineage_observed_date", "date")],
    "METADATA_DATA_ACCESS": [("workspace_table_key", "string"), ("access_observed_date", "date")],
    "METADATA_PIPELINE_RUN": [("workspace_pipeline_key", "string"), ("run_date", "date")],
    "METADATA_GUARDRAIL_RESULTS": [
        ("workspace_table_key", "string"),
        ("contract_key", "string"),
        ("guardrail_date", "date"),
    ],
    "METADATA_PROCESSING_STATE": [
        ("source_workspace_table_key", "string"),
        ("target_workspace_table_key", "string"),
        ("workspace_pipeline_key", "string"),
        ("observation_date", "date"),
    ],
}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False))


def stable_id(*parts: str, length: int = 20) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:length]


def lineage_tag(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "fabricops-powerbi:" + "|".join(parts)))


def tmdl_name(name: str) -> str:
    if name.replace("_", "").isalnum() and " " not in name and not name[0].isdigit():
        return name
    return "'" + name.replace("'", "''") + "'"


def schema_details() -> dict[str, dict[str, object]]:
    details: dict[str, dict[str, object]] = {}
    for table_name, schema in metadata_table_schema_registry().items():
        scalars = []
        complex_columns = []
        for field in schema.fields:
            data_type = field.dataType
            if hasattr(data_type, "fields") or hasattr(data_type, "elementType"):
                complex_columns.append(field.name)
            else:
                scalars.append((field.name, metadata_schema_type_name(data_type)))
        details[table_name] = {
            "owner": metadata_table_owner(table_name),
            "scalars": scalars,
            "complex": complex_columns,
        }
    return details


def m_add_keys(table_name: str) -> tuple[list[str], str]:
    steps: list[str] = []
    previous = "Typed"

    def add(step: str, column: str, expression: str) -> None:
        nonlocal previous
        steps.append(f'    {step} = Table.AddColumn({previous}, "{column}", each {expression}, type text),')
        previous = step

    def add_date(step: str, column: str, source: str) -> None:
        nonlocal previous
        steps.append(f'    {step} = Table.AddColumn({previous}, "{column}", each Date.From([{source}]), type date),')
        previous = step

    def key(*fields: str) -> str:
        values = ", ".join(f"[{field}]" for field in fields)
        return f'Text.Combine(List.Transform({{{values}}}, each if _ = null then "" else Text.From(_)), "|")'

    if table_name == "METADATA_DATA_AGREEMENT":
        add("WithAgreementKey", "agreement_key", key("agreement_id", "agreement_version"))
    elif table_name == "METADATA_DATA_CONTRACT":
        add("WithContractKey", "contract_key", key("contract_id", "contract_version"))
        add_date("WithContractDate", "contract_committed_date", "_committed_at")
    elif table_name in {"METADATA_DATA_CATALOGUE", "METADATA_DATA_PROFILED", "METADATA_DATA_PROFILED_FREQUENCY"}:
        add("WithTableKey", "workspace_table_key", key("workspace_id", "table_id"))
        add("WithColumnKey", "workspace_column_key", key("workspace_id", "table_id", "column_id"))
        date_step = {
            "METADATA_DATA_CATALOGUE": ("WithCatalogueDate", "catalogue_committed_date"),
            "METADATA_DATA_PROFILED": ("WithProfileDate", "profile_date"),
            "METADATA_DATA_PROFILED_FREQUENCY": ("WithFrequencyDate", "frequency_profile_date"),
        }[table_name]
        add_date(date_step[0], date_step[1], "_committed_at")
    elif table_name in {"METADATA_DATA_LINEAGE", "METADATA_DATA_ACCESS"}:
        add("WithTableKey", "workspace_table_key", key("workspace_id", "table_id"))
        if table_name == "METADATA_DATA_LINEAGE":
            add_date("WithLineageDate", "lineage_observed_date", "_committed_at")
        else:
            add_date("WithAccessDate", "access_observed_date", "_committed_at")
    elif table_name == "METADATA_PIPELINE_RUN":
        add("WithPipelineKey", "workspace_pipeline_key", key("workspace_id", "pipeline_id"))
        add_date("WithRunDate", "run_date", "started_at")
    elif table_name == "METADATA_GUARDRAIL_RESULTS":
        add("WithTableKey", "workspace_table_key", key("workspace_id", "table_id"))
        add("WithContractKey", "contract_key", key("contract_id", "contract_version"))
        add_date("WithGuardrailDate", "guardrail_date", "_committed_at")
    elif table_name == "METADATA_PROCESSING_STATE":
        add("WithSourceTableKey", "source_workspace_table_key", key("workspace_id", "source_table_id"))
        add("WithTargetTableKey", "target_workspace_table_key", key("workspace_id", "target_table_id"))
        add("WithPipelineKey", "workspace_pipeline_key", key("workspace_id", "pipeline_id"))
        add_date("WithObservationDate", "observation_date", "observed_at")
    return steps, previous


def generate_table_tmdl(table_name: str, detail: dict[str, object]) -> str:
    scalar_columns: list[tuple[str, str]] = detail["scalars"]  # type: ignore[assignment]
    all_columns = scalar_columns + KEY_COLUMNS.get(table_name, [])
    lines = [f"table {tmdl_name(table_name)}", f"\tlineageTag: {lineage_tag(table_name)}", ""]
    for column_name, kind in all_columns:
        tmdl_type = TYPE_MAP[kind][0]
        lines.extend(
            [
                f"\tcolumn {tmdl_name(column_name)}",
                f"\t\tdataType: {tmdl_type}",
                f"\t\tlineageTag: {lineage_tag(table_name, column_name)}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {column_name}",
            ]
        )
        if kind == "date":
            lines.append("\t\tformatString: yyyy-MM-dd")
        elif kind == "timestamp":
            lines.append("\t\tformatString: yyyy-MM-dd HH:mm:ss")
        if column_name in {item[0] for item in KEY_COLUMNS.get(table_name, [])}:
            lines.append("\t\tisHidden")
        lines.extend(["", "\t\tannotation SummarizationSetBy = Automatic", ""])

    columns_literal = ", ".join(f'"{name}"' for name, _ in scalar_columns)
    type_pairs = ", ".join(f'{{"{name}", {TYPE_MAP[kind][1]}}}' for name, kind in scalar_columns)
    complex_flag = "true" if detail["complex"] else "false"
    key_steps, final_step = m_add_keys(table_name)
    m_lines = [
        "let",
        f'    Source = FabricOpsSqlTable({"pGovernanceSchema" if detail["owner"] == "governance" else "pEngineeringSchema"}, "{table_name}", {{{columns_literal}}}, {complex_flag}),',
        f"    Typed = Table.TransformColumnTypes(Source, {{{type_pairs}}}),",
        *key_steps,
        f"    Result = {final_step}",
        "in",
        "    Result",
    ]
    lines.extend(
        [
            f"\tpartition {tmdl_name(table_name)} = m",
            "\t\tmode: import",
            "\t\tqueryGroup: 'Canonical metadata'",
            "\t\tsource = ```",
            *["\t\t\t" + line for line in m_lines],
            "\t\t\t```",
            "",
            "\tannotation PBI_NavigationStepName = Navigation",
            "",
            "\tannotation PBI_ResultType = Table",
        ]
    )
    return "\n".join(lines)


MEASURES = [
    ("Registered Tables", "COUNTROWS(DimTable)", "#,0", "Overview"),
    ("Active Tables", "CALCULATE(COUNTROWS(DimTable), DimTable[is_active] = TRUE())", "#,0", "Overview"),
    ("Registered Workspaces", "DISTINCTCOUNT(DimWorkspace[workspace_id])", "#,0", "Overview"),
    (
        "Frozen Contracts",
        'CALCULATE(DISTINCTCOUNT(METADATA_DATA_CONTRACT[contract_key]), METADATA_DATA_CONTRACT[status] = "Frozen")',
        "#,0",
        "Governance",
    ),
    (
        "Draft Contracts",
        'CALCULATE(DISTINCTCOUNT(METADATA_DATA_CONTRACT[contract_key]), METADATA_DATA_CONTRACT[status] = "Draft")',
        "#,0",
        "Governance",
    ),
    ("Pipeline Executions", "DISTINCTCOUNT(METADATA_PIPELINE_RUN[run_id])", "#,0", "Pipeline Operations"),
    (
        "Successful Runs",
        'CALCULATE([Pipeline Executions], LOWER(METADATA_PIPELINE_RUN[status]) IN {"succeeded", "success", "completed"})',
        "#,0",
        "Pipeline Operations",
    ),
    (
        "Failed Runs",
        'CALCULATE([Pipeline Executions], LOWER(METADATA_PIPELINE_RUN[status]) IN {"failed", "failure", "error"})',
        "#,0",
        "Pipeline Operations",
    ),
    ("Pipeline Success Rate", "DIVIDE([Successful Runs], [Pipeline Executions])", "0.0%", "Pipeline Operations"),
    (
        "Average Run Duration Seconds",
        "AVERAGEX(FILTER(METADATA_PIPELINE_RUN, NOT ISBLANK(METADATA_PIPELINE_RUN[completed_at])), DATEDIFF(METADATA_PIPELINE_RUN[started_at], METADATA_PIPELINE_RUN[completed_at], SECOND))",
        "#,0.0",
        "Pipeline Operations",
    ),
    ("Profile Observations", "DISTINCTCOUNT(METADATA_DATA_PROFILED[profile_id])", "#,0", "Data Quality"),
    ("Profile Snapshots", "DISTINCTCOUNT(METADATA_DATA_PROFILED[profile_snapshot_id])", "#,0", "Data Quality"),
    (
        "Weighted Null Percent",
        "DIVIDE(SUM(METADATA_DATA_PROFILED[null_count]), SUM(METADATA_DATA_PROFILED[row_count]))",
        "0.00%",
        "Data Quality",
    ),
    (
        "Average Distinct Percent",
        "DIVIDE(AVERAGE(METADATA_DATA_PROFILED[distinct_percent]), 100)",
        "0.00%",
        "Data Quality",
    ),
    ("Frequent Values", "COUNTROWS(METADATA_DATA_PROFILED_FREQUENCY)", "#,0", "Data Quality"),
    ("Guardrail Results", "DISTINCTCOUNT(METADATA_GUARDRAIL_RESULTS[guardrail_result_id])", "#,0", "Data Quality"),
    (
        "Guardrail Passed",
        'CALCULATE([Guardrail Results], LOWER(METADATA_GUARDRAIL_RESULTS[status]) IN {"passed", "pass", "success", "succeeded", "compliant"})',
        "#,0",
        "Data Quality",
    ),
    (
        "Guardrail Failed",
        'CALCULATE([Guardrail Results], LOWER(METADATA_GUARDRAIL_RESULTS[status]) IN {"failed", "fail", "failure", "noncompliant"})',
        "#,0",
        "Data Quality",
    ),
    ("Guardrail Pass Rate", "DIVIDE([Guardrail Passed], [Guardrail Results])", "0.0%", "Data Quality"),
    ("Data Quality Indicators", "[Profile Observations] + [Guardrail Results]", "#,0", "Overview"),
    (
        "Active Stewards",
        "CALCULATE(DISTINCTCOUNT(METADATA_DATA_STEWARD[steward_id]), METADATA_DATA_STEWARD[is_active] = TRUE())",
        "#,0",
        "Governance",
    ),
    (
        "Steward Coverage",
        "DIVIDE(DISTINCTCOUNT(METADATA_DATA_AGREEMENT[provider_steward_id]) + DISTINCTCOUNT(METADATA_DATA_AGREEMENT[recipient_steward_id]), 2 * [Active Stewards])",
        "0.0%",
        "Governance",
    ),
    ("Agreements", "DISTINCTCOUNT(METADATA_DATA_AGREEMENT[agreement_key])", "#,0", "Governance"),
    (
        "Agreements Expiring 30 Days",
        "CALCULATE([Agreements], METADATA_DATA_AGREEMENT[expiry_date] >= TODAY(), METADATA_DATA_AGREEMENT[expiry_date] <= TODAY() + 30)",
        "#,0",
        "Governance",
    ),
    ("Lineage Participations", "DISTINCTCOUNT(METADATA_DATA_LINEAGE[lineage_id])", "#,0", "Lineage & Access"),
    (
        "Source Participations",
        'CALCULATE([Lineage Participations], LOWER(METADATA_DATA_LINEAGE[pipeline_role]) = "source")',
        "#,0",
        "Lineage & Access",
    ),
    (
        "Target Participations",
        'CALCULATE([Lineage Participations], LOWER(METADATA_DATA_LINEAGE[pipeline_role]) = "target")',
        "#,0",
        "Lineage & Access",
    ),
    ("Observed Permissions", "DISTINCTCOUNT(METADATA_DATA_ACCESS[access_id])", "#,0", "Lineage & Access"),
    ("Observed Principals", "DISTINCTCOUNT(METADATA_DATA_ACCESS[user_principal])", "#,0", "Lineage & Access"),
    (
        "Committed Processing Records",
        'CALCULATE(DISTINCTCOUNT(METADATA_PROCESSING_STATE[record_id]), LOWER(METADATA_PROCESSING_STATE[status]) = "committed")',
        "#,0",
        "Pipeline Operations",
    ),
    (
        "Publication Receipts",
        'CALCULATE(DISTINCTCOUNT(METADATA_PROCESSING_STATE[record_id]), LOWER(METADATA_PROCESSING_STATE[record_type]) = "publication_receipt")',
        "#,0",
        "Pipeline Operations",
    ),
    ("Latest Profile At", "MAX(METADATA_DATA_CATALOGUE[last_profiled_at])", "yyyy-MM-dd HH:mm", "Data Catalogue"),
    (
        "Days Since Latest Profile",
        "VAR LastProfile = [Latest Profile At] RETURN IF(NOT ISBLANK(LastProfile), DATEDIFF(LastProfile, TODAY(), DAY))",
        "#,0",
        "Data Catalogue",
    ),
]


def generate_measures_tmdl() -> str:
    lines = ["table _Measures", f"\tlineageTag: {lineage_tag('_Measures')}", ""]
    for name, dax, fmt, folder in MEASURES:
        lines.extend(
            [
                f"\tmeasure {tmdl_name(name)} = ```",
                f"\t\t\t{dax}",
                "\t\t\t```",
                f"\t\tformatString: {fmt}",
                f"\t\tdisplayFolder: {folder}",
                f"\t\tlineageTag: {lineage_tag('_Measures', name)}",
                "",
            ]
        )
    lines.extend(
        [
            "\tcolumn Value",
            "\t\tdataType: int64",
            "\t\tisHidden",
            f"\t\tlineageTag: {lineage_tag('_Measures', 'Value')}",
            "\t\tsummarizeBy: none",
            "",
            "\tpartition _Measures = calculated",
            "\t\tmode: import",
            "\t\tsource = { 0 }",
        ]
    )
    return "\n".join(lines)


def generate_dimension_tmdls() -> dict[str, str]:
    date = f"""table Date
\tlineageTag: {lineage_tag("Date")}
\tdataCategory: Time

\tcolumn Date
\t\tdataType: dateTime
\t\tformatString: yyyy-MM-dd
\t\tlineageTag: {lineage_tag("Date", "Date")}
\t\tsummarizeBy: none
\t\tisKey

\tcolumn Year = YEAR([Date])
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: {lineage_tag("Date", "Year")}
\t\tsummarizeBy: none

\tcolumn Month = FORMAT([Date], "MMM")
\t\tdataType: string
\t\tsortByColumn: 'Month Number'
\t\tlineageTag: {lineage_tag("Date", "Month")}
\t\tsummarizeBy: none

\tcolumn 'Month Number' = MONTH([Date])
\t\tdataType: int64
\t\tisHidden
\t\tlineageTag: {lineage_tag("Date", "Month Number")}
\t\tsummarizeBy: none

\tcolumn 'Year Month' = FORMAT([Date], "yyyy-MM")
\t\tdataType: string
\t\tlineageTag: {lineage_tag("Date", "Year Month")}
\t\tsummarizeBy: none

\tpartition Date = calculated
\t\tmode: import
\t\tsource = CALENDAR(DATE(2020, 1, 1), DATE(2035, 12, 31))
"""
    dim_table_columns = [
        ("workspace_table_key", "string", True),
        ("workspace_id", "string", False),
        ("table_id", "string", False),
        ("table_name", "string", False),
        ("layer", "string", False),
        ("store_type", "string", False),
        ("schema_name", "string", False),
        ("is_active", "boolean", False),
        ("writer_workspace_id", "string", False),
        ("writer_notebook_name", "string", False),
        ("last_profiled_at", "dateTime", False),
    ]
    lines = ["table DimTable", f"\tlineageTag: {lineage_tag('DimTable')}", ""]
    for name, kind, hidden in dim_table_columns:
        lines.extend(
            [
                f"\tcolumn {tmdl_name(name)}",
                f"\t\tdataType: {kind}",
                f"\t\tlineageTag: {lineage_tag('DimTable', name)}",
                "\t\tsummarizeBy: none",
                f"\t\tsourceColumn: {name}",
            ]
        )
        if hidden:
            lines.append("\t\tisHidden")
        lines.extend(["", "\t\tannotation SummarizationSetBy = Automatic", ""])
    dim_table_m = """let
    Source = METADATA_DATA_CATALOGUE,
    TableRows = Table.SelectRows(Source, each Text.Lower(Text.From([metadata_level])) = "table"),
    Selected = Table.SelectColumns(TableRows, {"workspace_table_key", "workspace_id", "table_id", "table_name", "layer", "store_type", "schema_name", "is_active", "writer_workspace_id", "writer_notebook_name", "last_profiled_at"}),
    Result = Table.Distinct(Selected, {"workspace_table_key"})
in
    Result"""
    lines.extend(
        [
            "\tpartition DimTable = m",
            "\t\tmode: import",
            "\t\tqueryGroup: 'Semantic dimensions'",
            "\t\tsource = ```",
            *["\t\t\t" + x for x in dim_table_m.splitlines()],
            "\t\t\t```",
        ]
    )
    dim_table = "\n".join(lines)

    dim_workspace = f"""table DimWorkspace
\tlineageTag: {lineage_tag("DimWorkspace")}

\tcolumn workspace_id
\t\tdataType: string
\t\tlineageTag: {lineage_tag("DimWorkspace", "workspace_id")}
\t\tsummarizeBy: none
\t\tsourceColumn: workspace_id

\tpartition DimWorkspace = m
\t\tmode: import
\t\tqueryGroup: 'Semantic dimensions'
\t\tsource = ```
\t\t\tlet
\t\t\t    Source = DimTable,
\t\t\t    Result = Table.Distinct(Table.SelectColumns(Source, {{"workspace_id"}}))
\t\t\tin
\t\t\t    Result
\t\t\t```
"""
    dim_pipeline = f"""table DimPipeline
\tlineageTag: {lineage_tag("DimPipeline")}

\tcolumn workspace_pipeline_key
\t\tdataType: string
\t\tisHidden
\t\tlineageTag: {lineage_tag("DimPipeline", "workspace_pipeline_key")}
\t\tsummarizeBy: none
\t\tsourceColumn: workspace_pipeline_key

\tcolumn workspace_id
\t\tdataType: string
\t\tlineageTag: {lineage_tag("DimPipeline", "workspace_id")}
\t\tsummarizeBy: none
\t\tsourceColumn: workspace_id

\tcolumn pipeline_id
\t\tdataType: string
\t\tlineageTag: {lineage_tag("DimPipeline", "pipeline_id")}
\t\tsummarizeBy: none
\t\tsourceColumn: pipeline_id

\tpartition DimPipeline = m
\t\tmode: import
\t\tqueryGroup: 'Semantic dimensions'
\t\tsource = ```
\t\t\tlet
\t\t\t    Source = METADATA_PIPELINE_RUN,
\t\t\t    Selected = Table.SelectColumns(Source, {{"workspace_pipeline_key", "workspace_id", "pipeline_id"}}),
\t\t\t    Result = Table.Distinct(Selected, {{"workspace_pipeline_key"}})
\t\t\tin
\t\t\t    Result
\t\t\t```
"""
    return {"Date": date, "DimTable": dim_table, "DimWorkspace": dim_workspace, "DimPipeline": dim_pipeline}


RELATIONSHIPS = [
    ("DimWorkspace.workspace_id", "DimTable.workspace_id", True),
    ("DimWorkspace.workspace_id", "METADATA_PIPELINE_RUN.workspace_id", True),
    ("DimTable.workspace_table_key", "METADATA_DATA_CATALOGUE.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_DATA_PROFILED.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_DATA_PROFILED_FREQUENCY.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_DATA_LINEAGE.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_DATA_ACCESS.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_GUARDRAIL_RESULTS.workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_PROCESSING_STATE.source_workspace_table_key", True),
    ("DimTable.workspace_table_key", "METADATA_PROCESSING_STATE.target_workspace_table_key", False),
    ("DimPipeline.workspace_pipeline_key", "METADATA_PIPELINE_RUN.workspace_pipeline_key", True),
    ("DimPipeline.workspace_pipeline_key", "METADATA_PROCESSING_STATE.workspace_pipeline_key", True),
    ("METADATA_DATA_CONTRACT.contract_key", "METADATA_GUARDRAIL_RESULTS.contract_key", True),
    ("METADATA_DATA_STEWARD.steward_id", "METADATA_DATA_AGREEMENT.provider_steward_id", True),
    ("METADATA_DATA_STEWARD.steward_id", "METADATA_DATA_AGREEMENT.recipient_steward_id", False),
    ("Date.Date", "METADATA_PIPELINE_RUN.run_date", True),
    ("Date.Date", "METADATA_DATA_PROFILED.profile_date", True),
    ("Date.Date", "METADATA_DATA_PROFILED_FREQUENCY.frequency_profile_date", True),
    ("Date.Date", "METADATA_GUARDRAIL_RESULTS.guardrail_date", True),
    ("Date.Date", "METADATA_PROCESSING_STATE.observation_date", True),
    ("Date.Date", "METADATA_DATA_ACCESS.access_observed_date", True),
    ("Date.Date", "METADATA_DATA_LINEAGE.lineage_observed_date", True),
    ("Date.Date", "METADATA_DATA_CATALOGUE.catalogue_committed_date", True),
    ("Date.Date", "METADATA_DATA_CONTRACT.contract_committed_date", True),
    ("Date.Date", "METADATA_DATA_AGREEMENT.start_date", True),
]


def column_ref(value: str) -> str:
    table, column = value.split(".", 1)
    return f"{tmdl_name(table)}.{tmdl_name(column)}"


def generate_relationships_tmdl() -> str:
    blocks = []
    for index, (one, many, active) in enumerate(RELATIONSHIPS):
        block = [f"relationship {lineage_tag('relationship', str(index))}"]
        if not active:
            block.append("\tisActive: false")
        block.extend([f"\tfromColumn: {column_ref(many)}", f"\ttoColumn: {column_ref(one)}"])
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def generate_expressions_tmdl() -> str:
    function_m = """(SchemaName as text, TableName as text, ScalarColumns as list, HasComplexColumns as logical) as table =>
let
    EmptyProjection = #table(ScalarColumns, {}),
    DatabaseSource = Sql.Database(pSqlEndpoint, pDatabaseName, [CreateNavigationProperties=false, CommandTimeout=#duration(0, 0, 30, 0)]),
    QuotedColumns = Text.Combine(List.Transform(ScalarColumns, each "[" & Text.Replace(_, "]", "]]") & "]"), ", "),
    SqlText = "SELECT " & QuotedColumns & " FROM [" & Text.Replace(SchemaName, "]", "]]") & "].[" & Text.Replace(TableName, "]", "]]") & "]",
    Result = if HasComplexColumns and not pLoadComplexBearingTables then EmptyProjection else Value.NativeQuery(DatabaseSource, SqlText, null, [EnableFolding=true])
in
    Result"""
    params = [
        ("pSqlEndpoint", '"your-endpoint.datawarehouse.fabric.microsoft.com"', "Text"),
        ("pDatabaseName", '"your-metadata-lakehouse"', "Text"),
        ("pGovernanceSchema", '"governance"', "Text"),
        ("pEngineeringSchema", '"engineering"', "Text"),
        ("pLoadComplexBearingTables", "true", "Logical"),
    ]
    lines = []
    for name, value, kind in params:
        lines.extend(
            [
                f'expression {name} = {value} meta [IsParameterQuery=true, Type="{kind}", IsParameterQueryRequired=true]',
                f"\tlineageTag: {lineage_tag('expression', name)}",
                "\tqueryGroup: Parameters",
                "",
                "\tannotation PBI_NavigationStepName = Navigation",
                "",
                f"\tannotation PBI_ResultType = {kind}",
                "",
            ]
        )
    lines.extend(
        [
            "expression FabricOpsSqlTable = ```",
            *["\t" + line for line in function_m.splitlines()],
            "\t```",
            f"\tlineageTag: {lineage_tag('expression', 'FabricOpsSqlTable')}",
            "\tqueryGroup: 'Connection helpers'",
            "",
            "\tannotation PBI_ResultType = Function",
        ]
    )
    return "\n".join(lines)


def generate_model_tmdl(table_names: list[str]) -> str:
    query_order = table_names + [
        "DimTable",
        "DimWorkspace",
        "DimPipeline",
        "pSqlEndpoint",
        "pDatabaseName",
        "pGovernanceSchema",
        "pEngineeringSchema",
        "pLoadComplexBearingTables",
    ]
    lines = [
        "model FabricOpsMetadata",
        "\tculture: en-US",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        "\tdiscourageImplicitMeasures",
        "\tsourceQueryCulture: en-US",
        "\tdataAccessOptions",
        "\t\tlegacyRedirects",
        "\t\treturnErrorValuesAsNull",
        "",
        "queryGroup Parameters",
        "\tannotation PBI_QueryGroupOrder = 0",
        "",
        "queryGroup 'Connection helpers'",
        "\tannotation PBI_QueryGroupOrder = 1",
        "",
        "queryGroup 'Canonical metadata'",
        "\tannotation PBI_QueryGroupOrder = 2",
        "",
        "queryGroup 'Semantic dimensions'",
        "\tannotation PBI_QueryGroupOrder = 3",
        "",
        "annotation __PBI_TimeIntelligenceEnabled = 0",
        "",
        "annotation PBI_QueryOrder = " + json.dumps(query_order, separators=(",", ":")),
        "",
    ]
    for name in table_names + ["Date", "DimTable", "DimWorkspace", "DimPipeline", "_Measures"]:
        lines.append(f"ref table {tmdl_name(name)}")
    return "\n".join(lines)


def literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def field_projection(
    entity: str, property_name: str, *, measure: bool = False, display_name: str | None = None
) -> dict:
    kind = "Measure" if measure else "Column"
    projection = {
        "field": {kind: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": property_name}},
        "queryRef": f"{entity}.{property_name}",
        "nativeQueryRef": display_name or property_name,
    }
    if display_name:
        projection["displayName"] = display_name
    return projection


def container(title: str, *, show_title: bool = True) -> dict:
    return {
        "background": [{"properties": {"show": literal("true"), "transparency": literal("0D")}}],
        "border": [{"properties": {"show": literal("true"), "radius": literal("8D")}}],
        "title": [
            {
                "properties": {
                    "show": literal("true" if show_title else "false"),
                    "text": literal(repr(title)),
                    "fontSize": literal("11D"),
                    "bold": literal("true"),
                }
            }
        ],
        "visualHeader": [{"properties": {"show": literal("true")}}],
    }


def visual_base(page_id: str, kind: str, index: int, x: float, y: float, width: float, height: float) -> dict:
    name = stable_id(page_id, kind, str(index))
    return {
        "$schema": f"{SCHEMA_URL}/visualContainer/2.7.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": index, "height": height, "width": width, "tabOrder": index},
        "visual": {"visualType": kind, "drillFilterOtherVisuals": True},
    }


def textbox(
    page_id: str,
    index: int,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: int = 12,
    color: str = COLORS["ink"],
    bold: bool = False,
    background: bool = False,
) -> dict:
    payload = visual_base(page_id, "textbox", index, x, y, width, height)
    payload["visual"]["objects"] = {
        "general": [
            {
                "properties": {
                    "paragraphs": [
                        {
                            "textRuns": [
                                {
                                    "value": text,
                                    "textStyle": {
                                        "fontSize": f"{size}pt",
                                        "fontFamily": "Segoe UI",
                                        "color": color,
                                        "fontWeight": "bold" if bold else "normal",
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    payload["visual"]["visualContainerObjects"] = {
        "background": [{"properties": {"show": literal("true" if background else "false")}}],
        "border": [{"properties": {"show": literal("false")}}],
    }
    return payload


def card(
    page_id: str, index: int, title: str, measure: str, x: float, y: float, width: float = 155, height: float = 86
) -> dict:
    payload = visual_base(page_id, "card", index, x, y, width, height)
    payload["visual"]["query"] = {
        "queryState": {"Values": {"projections": [field_projection("_Measures", measure, measure=True)]}}
    }
    payload["visual"]["objects"] = {
        "labels": [
            {
                "properties": {
                    "fontSize": literal("22D"),
                    "fontColor": {"solid": {"color": literal(repr(COLORS["navy"]))}},
                }
            }
        ]
    }
    payload["visual"]["visualContainerObjects"] = container(title)
    return payload


def slicer(
    page_id: str,
    index: int,
    title: str,
    entity: str,
    column: str,
    x: float,
    y: float,
    width: float = 175,
    height: float = 62,
) -> dict:
    payload = visual_base(page_id, "slicer", index, x, y, width, height)
    payload["visual"]["query"] = {"queryState": {"Values": {"projections": [field_projection(entity, column)]}}}
    payload["visual"]["objects"] = {
        "data": [{"properties": {"mode": literal("'Dropdown'")}}],
        "selection": [{"properties": {"selectAllCheckboxEnabled": literal("true")}}],
    }
    payload["visual"]["visualContainerObjects"] = container(title)
    return payload


def data_visual(
    page_id: str,
    index: int,
    kind: str,
    title: str,
    roles: dict[str, list[tuple[str, str, bool, str | None]]],
    x: float,
    y: float,
    width: float,
    height: float,
) -> dict:
    payload = visual_base(page_id, kind, index, x, y, width, height)
    query_state = {}
    for role, fields in roles.items():
        query_state[role] = {
            "projections": [
                field_projection(entity, prop, measure=is_measure, display_name=display_name)
                for entity, prop, is_measure, display_name in fields
            ]
        }
    payload["visual"]["query"] = {"queryState": query_state}
    payload["visual"]["visualContainerObjects"] = container(title)
    if kind in {"lineChart", "columnChart"}:
        payload["visual"]["objects"] = {
            "legend": [{"properties": {"show": literal("true"), "position": literal("'Top'")}}],
            "dataPoint": [{"properties": {"fill": {"solid": {"color": literal(repr(COLORS["blue"]))}}}}],
        }
    elif kind == "tableEx":
        payload["visual"]["objects"] = {
            "grid": [{"properties": {"gridVertical": literal("false"), "rowPadding": literal("4D")}}],
            "values": [{"properties": {"fontSize": literal("9D")}}],
            "columnHeaders": [{"properties": {"fontSize": literal("9D"), "bold": literal("true")}}],
        }
    return payload


def nav_button(page_id: str, index: int, title: str, target_page_id: str, y: float, selected: bool) -> dict:
    payload = visual_base(page_id, "actionButton", index, 12, y, 146, 38)
    payload["visual"]["objects"] = {
        "text": [
            {
                "properties": {
                    "show": literal("true"),
                    "text": literal(repr(title)),
                    "fontSize": literal("10D"),
                    "bold": literal("true" if selected else "false"),
                    "fontColor": {
                        "solid": {"color": literal(repr(COLORS["white"] if selected else COLORS["blue_light"]))}
                    },
                }
            }
        ],
        "fill": [
            {
                "properties": {
                    "show": literal("true"),
                    "fillColor": {"solid": {"color": literal(repr(COLORS["purple"] if selected else COLORS["navy"]))}},
                }
            }
        ],
        "outline": [{"properties": {"show": literal("false")}}],
        "shape": [{"properties": {"roundEdge": literal("6D")}}],
    }
    payload["visual"]["visualContainerObjects"] = {
        "visualLink": [
            {
                "properties": {
                    "show": literal("true"),
                    "type": literal("'PageNavigation'"),
                    "navigationSection": literal(repr(target_page_id)),
                    "tooltip": literal(repr(title)),
                }
            }
        ],
        "title": [{"properties": {"show": literal("false")}}],
        "background": [{"properties": {"show": literal("false")}}],
        "border": [{"properties": {"show": literal("false")}}],
    }
    return payload


PAGE_SPECS = [
    ("01 — Overview", "Operational posture across registered assets, governance, execution and data quality."),
    ("02 — Data Catalogue", "Current workspace-scoped table and column inventory with profile freshness."),
    ("03 — Governance", "Stewards, Agreement windows, Contract versions and aggregate Guardrail posture."),
    ("04 — Data Quality", "Historical column profiling, frequent values and persisted Guardrail outcomes."),
    ("05 — Pipeline Operations", "Execution history and scalar Processing State outcomes from persisted metadata."),
    ("06 — Lineage & Access", "Pipeline source/target participation and observed—not effective—permissions."),
]


def page_visuals(page_index: int, page_id: str, page_ids: list[str]) -> list[dict]:
    title, subtitle = PAGE_SPECS[page_index]
    sidebar = textbox(page_id, 0, "", 0, 0, 170, 720, background=True)
    sidebar["visual"]["visualContainerObjects"]["background"][0]["properties"] = {
        "show": literal("true"),
        "color": {"solid": {"color": literal(repr(COLORS["navy"]))}},
        "transparency": literal("0D"),
    }
    visuals: list[dict] = [
        sidebar,
        textbox(page_id, 1, "FabricOps", 12, 18, 146, 32, size=19, color=COLORS["white"], bold=True),
        textbox(page_id, 2, "METADATA", 12, 48, 146, 18, size=8, color=COLORS["blue_light"], bold=True),
        textbox(page_id, 3, title, 188, 18, 1060, 35, size=20, color=COLORS["navy"], bold=True),
        textbox(page_id, 4, subtitle, 188, 52, 1060, 25, size=10, color=COLORS["muted"]),
    ]
    for nav_index, ((nav_title, _), target_id) in enumerate(zip(PAGE_SPECS, page_ids), start=10):
        visuals.append(
            nav_button(
                page_id,
                nav_index,
                nav_title.split(" — ", 1)[1],
                target_id,
                92 + (nav_index - 10) * 48,
                nav_index - 10 == page_index,
            )
        )

    i = 30
    if page_index == 0:
        for x, title_, measure in [
            (188, "Registered tables", "Registered Tables"),
            (354, "Active tables", "Active Tables"),
            (520, "Workspaces", "Registered Workspaces"),
            (686, "Frozen contracts*", "Frozen Contracts"),
            (852, "Executions", "Pipeline Executions"),
            (1018, "Success rate", "Pipeline Success Rate"),
        ]:
            visuals.append(card(page_id, i, title_, measure, x, 92))
            i += 1
        visuals.extend(
            [
                card(page_id, i, "Failed runs", "Failed Runs", 188, 190, 155, 82),
                card(page_id, i + 1, "DQ indicators", "Data Quality Indicators", 354, 190, 155, 82),
                card(page_id, i + 2, "Null percent", "Weighted Null Percent", 520, 190, 155, 82),
                card(page_id, i + 3, "Guardrail pass", "Guardrail Pass Rate", 686, 190, 155, 82),
                data_visual(
                    page_id,
                    i + 4,
                    "lineChart",
                    "Pipeline executions over time",
                    {
                        "Category": [("Date", "Date", False, None)],
                        "Y": [
                            ("_Measures", "Pipeline Executions", True, "Executions"),
                            ("_Measures", "Failed Runs", True, "Failed"),
                        ],
                    },
                    188,
                    290,
                    520,
                    250,
                ),
                data_visual(
                    page_id,
                    i + 5,
                    "columnChart",
                    "Guardrail outcomes",
                    {
                        "Category": [("METADATA_GUARDRAIL_RESULTS", "status", False, None)],
                        "Y": [("_Measures", "Guardrail Results", True, "Results")],
                    },
                    726,
                    290,
                    522,
                    250,
                ),
                data_visual(
                    page_id,
                    i + 6,
                    "tableEx",
                    "Latest pipeline executions",
                    {
                        "Values": [
                            ("METADATA_PIPELINE_RUN", "started_at", False, None),
                            ("METADATA_PIPELINE_RUN", "pipeline_id", False, None),
                            ("METADATA_PIPELINE_RUN", "execution_mode", False, None),
                            ("METADATA_PIPELINE_RUN", "status", False, None),
                            ("METADATA_PIPELINE_RUN", "completed_at", False, None),
                        ]
                    },
                    188,
                    555,
                    1060,
                    135,
                ),
                textbox(
                    page_id,
                    i + 7,
                    "* Frozen Contract versions are shown because activation authority is nested in Registry approvals and is not scalar-queryable through the Lakehouse SQL analytics endpoint.",
                    852,
                    190,
                    396,
                    82,
                    size=9,
                    color=COLORS["purple"],
                ),
            ]
        )
    elif page_index == 1:
        visuals.extend(
            [
                slicer(page_id, i, "Workspace", "DimWorkspace", "workspace_id", 188, 92, 235),
                slicer(page_id, i + 1, "Layer", "DimTable", "layer", 435, 92, 190),
                slicer(page_id, i + 2, "Store type", "DimTable", "store_type", 637, 92, 190),
                slicer(page_id, i + 3, "Active state", "DimTable", "is_active", 839, 92, 190),
                card(page_id, i + 4, "Registered tables", "Registered Tables", 1041, 92, 207, 62),
                data_visual(
                    page_id,
                    i + 5,
                    "tableEx",
                    "Table inventory",
                    {
                        "Values": [
                            ("DimTable", "workspace_id", False, "Workspace"),
                            ("DimTable", "layer", False, None),
                            ("DimTable", "schema_name", False, "Schema"),
                            ("DimTable", "table_name", False, "Table"),
                            ("DimTable", "store_type", False, "Store"),
                            ("DimTable", "is_active", False, "Active"),
                            ("DimTable", "writer_notebook_name", False, "Writer notebook"),
                            ("DimTable", "last_profiled_at", False, "Last profiled"),
                        ]
                    },
                    188,
                    174,
                    1060,
                    230,
                ),
                data_visual(
                    page_id,
                    i + 6,
                    "tableEx",
                    "Column inventory",
                    {
                        "Values": [
                            ("METADATA_DATA_CATALOGUE", "table_name", False, "Table"),
                            ("METADATA_DATA_CATALOGUE", "column_name", False, "Column"),
                            ("METADATA_DATA_CATALOGUE", "data_type", False, "Data type"),
                            ("METADATA_DATA_CATALOGUE", "is_active", False, "Active"),
                            ("METADATA_DATA_CATALOGUE", "first_profiled_at", False, "First profiled"),
                            ("METADATA_DATA_CATALOGUE", "last_profiled_at", False, "Last profiled"),
                        ]
                    },
                    188,
                    420,
                    720,
                    270,
                ),
                card(page_id, i + 7, "Latest profile", "Latest Profile At", 926, 420, 322, 105),
                card(page_id, i + 8, "Days since latest", "Days Since Latest Profile", 926, 540, 322, 105),
            ]
        )
    elif page_index == 2:
        visuals.extend(
            [
                slicer(page_id, i, "Contract status", "METADATA_DATA_CONTRACT", "status", 188, 92, 220),
                slicer(page_id, i + 1, "Agreement domain", "METADATA_DATA_AGREEMENT", "domain", 420, 92, 220),
                slicer(page_id, i + 2, "Guardrail severity", "METADATA_GUARDRAIL_RESULTS", "severity", 652, 92, 220),
                card(page_id, i + 3, "Frozen contracts", "Frozen Contracts", 884, 92, 170, 62),
                card(page_id, i + 4, "Expiring in 30d", "Agreements Expiring 30 Days", 1066, 92, 182, 62),
                data_visual(
                    page_id,
                    i + 5,
                    "tableEx",
                    "Contract inventory and versions",
                    {
                        "Values": [
                            ("METADATA_DATA_CONTRACT", "contract_id", False, None),
                            ("METADATA_DATA_CONTRACT", "contract_version", False, "Version"),
                            ("METADATA_DATA_CONTRACT", "table_name", False, "Table"),
                            ("METADATA_DATA_CONTRACT", "status", False, None),
                            ("METADATA_DATA_CONTRACT", "_committed_at", False, "Committed"),
                        ]
                    },
                    188,
                    174,
                    600,
                    235,
                ),
                data_visual(
                    page_id,
                    i + 6,
                    "tableEx",
                    "Agreement inventory and expiry",
                    {
                        "Values": [
                            ("METADATA_DATA_AGREEMENT", "agreement_name", False, "Agreement"),
                            ("METADATA_DATA_AGREEMENT", "agreement_version", False, "Version"),
                            ("METADATA_DATA_AGREEMENT", "domain", False, None),
                            ("METADATA_DATA_AGREEMENT", "provider_steward_name", False, "Provider steward"),
                            ("METADATA_DATA_AGREEMENT", "recipient_steward_name", False, "Recipient steward"),
                            ("METADATA_DATA_AGREEMENT", "expiry_date", False, "Expiry"),
                        ]
                    },
                    806,
                    174,
                    442,
                    235,
                ),
                data_visual(
                    page_id,
                    i + 7,
                    "tableEx",
                    "Steward registry",
                    {
                        "Values": [
                            ("METADATA_DATA_STEWARD", "steward_name", False, "Steward"),
                            ("METADATA_DATA_STEWARD", "steward_role", False, "Role"),
                            ("METADATA_DATA_STEWARD", "contact", False, None),
                            ("METADATA_DATA_STEWARD", "is_active", False, "Active"),
                        ]
                    },
                    188,
                    425,
                    600,
                    265,
                ),
                data_visual(
                    page_id,
                    i + 8,
                    "columnChart",
                    "Governance status overview",
                    {
                        "Category": [("METADATA_GUARDRAIL_RESULTS", "status", False, None)],
                        "Y": [("_Measures", "Guardrail Results", True, "Guardrail results")],
                    },
                    806,
                    425,
                    442,
                    265,
                ),
            ]
        )
    elif page_index == 3:
        visuals.extend(
            [
                slicer(page_id, i, "Workspace", "DimWorkspace", "workspace_id", 188, 92, 215),
                slicer(page_id, i + 1, "Table", "DimTable", "table_name", 415, 92, 215),
                slicer(page_id, i + 2, "Date", "Date", "Date", 642, 92, 215),
                card(page_id, i + 3, "Null percent", "Weighted Null Percent", 869, 92, 180, 62),
                card(page_id, i + 4, "Guardrail pass", "Guardrail Pass Rate", 1061, 92, 187, 62),
                data_visual(
                    page_id,
                    i + 5,
                    "lineChart",
                    "Profiling history",
                    {
                        "Category": [("Date", "Date", False, None)],
                        "Y": [
                            ("_Measures", "Profile Observations", True, "Profile rows"),
                            ("_Measures", "Weighted Null Percent", True, "Null %"),
                        ],
                    },
                    188,
                    174,
                    520,
                    230,
                ),
                data_visual(
                    page_id,
                    i + 6,
                    "columnChart",
                    "Guardrail outcomes and trends",
                    {
                        "Category": [("METADATA_GUARDRAIL_RESULTS", "status", False, None)],
                        "Y": [("_Measures", "Guardrail Results", True, "Results")],
                    },
                    726,
                    174,
                    522,
                    230,
                ),
                data_visual(
                    page_id,
                    i + 7,
                    "tableEx",
                    "Column profile statistics",
                    {
                        "Values": [
                            ("METADATA_DATA_PROFILED", "table_name", False, "Table"),
                            ("METADATA_DATA_PROFILED", "column_name", False, "Column"),
                            ("METADATA_DATA_PROFILED", "row_count", False, "Rows"),
                            ("METADATA_DATA_PROFILED", "null_percent", False, "Null %"),
                            ("METADATA_DATA_PROFILED", "distinct_count", False, "Distinct"),
                            ("METADATA_DATA_PROFILED", "distinct_percent", False, "Distinct %"),
                            ("METADATA_DATA_PROFILED", "min_value", False, "Min"),
                            ("METADATA_DATA_PROFILED", "max_value", False, "Max"),
                        ]
                    },
                    188,
                    420,
                    650,
                    270,
                ),
                data_visual(
                    page_id,
                    i + 8,
                    "tableEx",
                    "Frequent values",
                    {
                        "Values": [
                            ("METADATA_DATA_PROFILED_FREQUENCY", "table_name", False, "Table"),
                            ("METADATA_DATA_PROFILED_FREQUENCY", "column_name", False, "Column"),
                            ("METADATA_DATA_PROFILED_FREQUENCY", "value", False, None),
                            ("METADATA_DATA_PROFILED_FREQUENCY", "frequency_count", False, "Count"),
                            ("METADATA_DATA_PROFILED_FREQUENCY", "frequency_percent", False, "%"),
                            ("METADATA_DATA_PROFILED_FREQUENCY", "frequency_rank", False, "Rank"),
                        ]
                    },
                    856,
                    420,
                    392,
                    270,
                ),
            ]
        )
    elif page_index == 4:
        visuals.extend(
            [
                slicer(page_id, i, "Execution mode", "METADATA_PIPELINE_RUN", "execution_mode", 188, 92, 205),
                slicer(page_id, i + 1, "Run status", "METADATA_PIPELINE_RUN", "status", 405, 92, 205),
                slicer(page_id, i + 2, "Date", "Date", "Date", 622, 92, 205),
                card(page_id, i + 3, "Executions", "Pipeline Executions", 839, 92, 125, 62),
                card(page_id, i + 4, "Success rate", "Pipeline Success Rate", 976, 92, 132, 62),
                card(page_id, i + 5, "Failed", "Failed Runs", 1120, 92, 128, 62),
                data_visual(
                    page_id,
                    i + 6,
                    "lineChart",
                    "Success and failure trend",
                    {
                        "Category": [("Date", "Date", False, None)],
                        "Y": [
                            ("_Measures", "Successful Runs", True, "Successful"),
                            ("_Measures", "Failed Runs", True, "Failed"),
                        ],
                    },
                    188,
                    174,
                    520,
                    220,
                ),
                data_visual(
                    page_id,
                    i + 7,
                    "columnChart",
                    "Persisted Processing State outcomes",
                    {
                        "Category": [("METADATA_PROCESSING_STATE", "record_type", False, "Record type")],
                        "Y": [("_Measures", "Committed Processing Records", True, "Committed")],
                    },
                    726,
                    174,
                    522,
                    220,
                ),
                data_visual(
                    page_id,
                    i + 8,
                    "tableEx",
                    "Execution history",
                    {
                        "Values": [
                            ("METADATA_PIPELINE_RUN", "run_id", False, "Run"),
                            ("METADATA_PIPELINE_RUN", "pipeline_id", False, "Pipeline"),
                            ("METADATA_PIPELINE_RUN", "execution_mode", False, "Mode"),
                            ("METADATA_PIPELINE_RUN", "workspace_id", False, "Workspace"),
                            ("METADATA_PIPELINE_RUN", "started_at", False, "Started"),
                            ("METADATA_PIPELINE_RUN", "completed_at", False, "Completed"),
                            ("METADATA_PIPELINE_RUN", "status", False, None),
                            ("METADATA_PIPELINE_RUN", "boundary_completed", False, "Boundary complete"),
                        ]
                    },
                    188,
                    410,
                    760,
                    280,
                ),
                textbox(
                    page_id,
                    i + 9,
                    "Connector boundary\n\nRegistry entries, Read/Write operation modes, stage outcomes, and loaded/already-loaded/skipped operation statuses are native ARRAY/STRUCT fields. They remain authoritative in Delta and are intentionally not flattened or duplicated. This scalar report shows run headers and Processing State only.",
                    968,
                    410,
                    280,
                    280,
                    size=10,
                    color=COLORS["purple"],
                    background=True,
                ),
            ]
        )
    else:
        visuals.extend(
            [
                slicer(page_id, i, "Workspace", "DimWorkspace", "workspace_id", 188, 92, 210),
                slicer(page_id, i + 1, "Pipeline role", "METADATA_DATA_LINEAGE", "pipeline_role", 410, 92, 210),
                slicer(page_id, i + 2, "Permission source", "METADATA_DATA_ACCESS", "permission_source", 632, 92, 210),
                card(page_id, i + 3, "Source participation", "Source Participations", 854, 92, 190, 62),
                card(page_id, i + 4, "Observed principals", "Observed Principals", 1056, 92, 192, 62),
                data_visual(
                    page_id,
                    i + 5,
                    "columnChart",
                    "Source and target participation",
                    {
                        "Category": [("METADATA_DATA_LINEAGE", "pipeline_role", False, "Role")],
                        "Y": [("_Measures", "Lineage Participations", True, "Participations")],
                    },
                    188,
                    174,
                    430,
                    220,
                ),
                data_visual(
                    page_id,
                    i + 6,
                    "columnChart",
                    "Permission source breakdown",
                    {
                        "Category": [("METADATA_DATA_ACCESS", "permission_source", False, "Source")],
                        "Y": [("_Measures", "Observed Permissions", True, "Permissions")],
                    },
                    636,
                    174,
                    430,
                    220,
                ),
                textbox(
                    page_id,
                    i + 7,
                    "Scope: lineage records pipeline source/target participation only. It does not assert transformation-level lineage. Access rows are observed permissions, not effective-access decisions.",
                    1084,
                    174,
                    164,
                    220,
                    size=9,
                    color=COLORS["purple"],
                    background=True,
                ),
                data_visual(
                    page_id,
                    i + 8,
                    "tableEx",
                    "Lineage participation",
                    {
                        "Values": [
                            ("METADATA_DATA_LINEAGE", "workspace_id", False, "Workspace"),
                            ("METADATA_DATA_LINEAGE", "table_name", False, "Table"),
                            ("METADATA_DATA_LINEAGE", "pipeline_role", False, "Role"),
                            ("METADATA_DATA_LINEAGE", "_notebook_name", False, "Observed notebook"),
                            ("METADATA_DATA_LINEAGE", "_committed_at", False, "Observed at"),
                        ]
                    },
                    188,
                    410,
                    510,
                    280,
                ),
                data_visual(
                    page_id,
                    i + 9,
                    "tableEx",
                    "Observed access permissions",
                    {
                        "Values": [
                            ("METADATA_DATA_ACCESS", "user_principal", False, "Principal"),
                            ("METADATA_DATA_ACCESS", "user_type", False, "Type"),
                            ("METADATA_DATA_ACCESS", "table_name", False, "Table"),
                            ("METADATA_DATA_ACCESS", "access_level", False, "Level"),
                            ("METADATA_DATA_ACCESS", "access_value", False, "Permission"),
                            ("METADATA_DATA_ACCESS", "access_state", False, "State"),
                            ("METADATA_DATA_ACCESS", "permission_source", False, "Source"),
                            ("METADATA_DATA_ACCESS", "role_name", False, "Role"),
                        ]
                    },
                    716,
                    410,
                    532,
                    280,
                ),
            ]
        )
    return visuals


def generate_report() -> None:
    page_ids = [stable_id("page", title) for title, _ in PAGE_SPECS]
    write_json(
        DEFINITION_ROOT / "version.json",
        {"$schema": f"{SCHEMA_URL}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"},
    )
    write_json(
        PAGES_ROOT / "pages.json",
        {
            "$schema": f"{SCHEMA_URL}/pagesMetadata/1.0.0/schema.json",
            "pageOrder": page_ids,
            "activePageName": page_ids[0],
        },
    )
    for index, ((title, _), page_id) in enumerate(zip(PAGE_SPECS, page_ids)):
        page_dir = PAGES_ROOT / page_id
        page = {
            "$schema": f"{SCHEMA_URL}/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": title,
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
            "objects": {
                "background": [
                    {
                        "properties": {
                            "color": {"solid": {"color": literal(repr(COLORS["canvas"]))}},
                            "transparency": literal("0D"),
                        }
                    }
                ],
                "outspace": [{"properties": {"color": {"solid": {"color": literal(repr(COLORS["canvas"]))}}}}],
            },
        }
        write_json(page_dir / "page.json", page)
        for visual in page_visuals(index, page_id, page_ids):
            write_json(page_dir / "visuals" / visual["name"] / "visual.json", visual)

    report = {
        "$schema": f"{SCHEMA_URL}/report/3.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY25SU12",
                "reportVersionAtImport": {"visual": "2.7.0", "report": "3.2.0", "page": "2.1.0"},
                "type": "SharedResources",
            },
            "customTheme": {
                "name": "FabricOpsTheme.json",
                "reportVersionAtImport": {"visual": "2.7.0", "report": "3.2.0", "page": "2.1.0"},
                "type": "RegisteredResources",
            },
        },
        "resourcePackages": [
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [{"name": "CY25SU12", "path": "BaseThemes/CY25SU12.json", "type": "BaseTheme"}],
            },
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [{"name": "FabricOpsTheme.json", "path": "FabricOpsTheme.json", "type": "CustomTheme"}],
            },
        ],
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True,
        },
    }
    write_json(DEFINITION_ROOT / "report.json", report)


def generate_theme() -> None:
    theme = {
        "name": "FabricOps",
        "$schema": "https://raw.githubusercontent.com/microsoft/powerbi-desktop-samples/main/Report%20Theme%20JSON%20Schema/reportThemeSchema-2.129.json",
        "dataColors": [
            COLORS["blue"],
            COLORS["purple"],
            COLORS["green"],
            COLORS["amber"],
            COLORS["red"],
            "#06B6D4",
            "#8B5CF6",
            "#64748B",
        ],
        "background": COLORS["canvas"],
        "foreground": COLORS["ink"],
        "tableAccent": COLORS["blue"],
        "textClasses": {
            "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 24, "color": COLORS["navy"]},
            "title": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": COLORS["ink"]},
            "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": COLORS["muted"]},
        },
        "visualStyles": {
            "*": {
                "*": {
                    "background": [{"show": True, "color": {"solid": {"color": COLORS["white"]}}, "transparency": 0}],
                    "border": [{"show": True, "color": {"solid": {"color": "#E2E8F0"}}, "radius": 8}],
                    "title": [
                        {
                            "show": True,
                            "fontFamily": "Segoe UI Semibold",
                            "fontSize": 11,
                            "fontColor": {"solid": {"color": COLORS["ink"]}},
                        }
                    ],
                    "visualHeader": [{"show": True}],
                }
            }
        },
    }
    write_json(REPORT_ROOT / "StaticResources" / "RegisteredResources" / "FabricOpsTheme.json", theme)


def generate_project() -> None:
    base_theme_path = REPORT_ROOT / "StaticResources" / "SharedResources" / "BaseThemes" / "CY25SU12.json"
    if not base_theme_path.exists():
        raise RuntimeError("Committed CY25SU12 base theme is missing; restore it before generation.")
    base_theme_text = base_theme_path.read_text(encoding="utf-8")
    if PROJECT_ROOT.exists():
        for child in (REPORT_ROOT, MODEL_ROOT):
            if child.exists():
                shutil.rmtree(child)
    details = schema_details()
    for table_name in CANONICAL_METADATA_TABLES:
        write_text(TABLES_ROOT / f"{table_name}.tmdl", generate_table_tmdl(table_name, details[table_name]))
    for name, content in generate_dimension_tmdls().items():
        write_text(TABLES_ROOT / f"{name}.tmdl", content)
    write_text(TABLES_ROOT / "_Measures.tmdl", generate_measures_tmdl())
    write_text(MODEL_ROOT / "definition" / "expressions.tmdl", generate_expressions_tmdl())
    write_text(MODEL_ROOT / "definition" / "relationships.tmdl", generate_relationships_tmdl())
    write_text(MODEL_ROOT / "definition" / "model.tmdl", generate_model_tmdl(list(CANONICAL_METADATA_TABLES)))
    write_text(
        MODEL_ROOT / "definition" / "database.tmdl",
        f"database FabricOpsMetadata\n\tid: {lineage_tag('database')}\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n\tlanguage: 1033",
    )
    write_json(
        MODEL_ROOT / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {},
        },
    )
    write_json(
        REPORT_ROOT / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../FabricOpsMetadata.SemanticModel"}},
        },
    )
    write_json(
        PROJECT_ROOT / "FabricOpsMetadata.pbip",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [{"report": {"path": "FabricOpsMetadata.Report"}}],
            "settings": {"enableAutoRecovery": True},
        },
    )
    generate_report()
    generate_theme()

    target_theme = REPORT_ROOT / "StaticResources" / "SharedResources" / "BaseThemes" / "CY25SU12.json"
    write_text(target_theme, base_theme_text)


if __name__ == "__main__":
    generate_project()
    print(f"Generated {PROJECT_ROOT.relative_to(REPO_ROOT)}")
