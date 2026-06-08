from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
PIPELINE_NOTEBOOK = ROOT / "templates" / "notebooks" / "02_pipeline.ipynb"


def _notebook_sources() -> tuple[str, str]:
    notebook = json.loads(PIPELINE_NOTEBOOK.read_text(encoding="utf-8"))
    markdown = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "markdown")
    code_cells = ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    for cell in code_cells:
        ast.parse("\n".join(line for line in cell.splitlines() if not line.lstrip().startswith("%")))
    return markdown, "\n".join(code_cells)


def test_pipeline_notebook_uses_existing_public_apis_and_metadata_helpers():
    markdown, code = _notebook_sources()

    for helper in [
        "read_lakehouse_csv",
        "profile_dataframe",
        "validate_schema",
        "monitor_data_changes",
        "enforce_dq_rules",
        "stop_if_failed",
        "write_lakehouse_table",
        "write_catalogue_evidence",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    ]:
        assert helper in code
    for removed_wrapper in [
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_data_drift_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    ]:
        assert removed_wrapper not in code

    assert "SOURCE_DEFINITIONS" not in code
    assert "USE_SAMPLE_DATA" not in code
    assert "sample_agreement_dataset" not in code
    assert "Files/sample/minimal_source.csv" not in code
    assert "SOURCE_DATASETS" in code
    assert 'source_config["df"]' in code
    assert "TARGET_DEFINITIONS" not in code
    assert "TARGET_DATASETS" in code
    assert 'target_config["df"]' in code
    assert "RUN_ID = RUN_CONTEXT.run_id" in code
    assert "RUN_CONTEXT.runtime_metadata.get" in code
    assert "SETUP." not in code
    assert "LINEAGE_RELATIONSHIPS" in code
    assert "METADATA_PIPELINE_RUNS" in markdown
    assert "imports existing FabricOps callables directly for reads, profiling, guardrails, and writes" in markdown
    assert (
        "Metadata evidence helpers are imported only where they hide catalogue, lineage, "
        "and runtime-summary plumbing"
        in markdown
    )


def test_pipeline_notebook_contains_expected_high_level_flow_sections():
    markdown, _ = _notebook_sources()
    expected_sections = [
        "## 1. Run `00_env_config`",
        "## 2. Import required functions",
        "## 3. Select data agreement and register notebook",
        "## 4. Read source data",
        "## 5. Register source DataFrames with FabricOps guardrails",
        "## 6. Profile each registered source DataFrame",
        "## 7. Check each source schema",
        "## 8. Check each source for data drift",
        "## 9. Check each source with DQ guardrails",
        "## 10. Write source catalogue evidence",
        "## 11. Transform to target DataFrame",
        "## 12. Register target outputs and add audit columns",
        "## 13. Check each target schema",
        "## 14. Check each target for data drift",
        "## 15. Check each target with DQ guardrails",
        "## 16. Write target catalogue evidence",
        "## 17. Write target tables",
        "## 18. Capture many-to-many lineage",
        "## 19. Write runtime summary",
    ]
    for section in expected_sections:
        assert section in markdown


def test_pipeline_notebook_hides_manual_catalogue_and_lineage_plumbing():
    _, code = _notebook_sources()

    forbidden_visible_plumbing = [
        "lineage_rows = []",
        "for row in lineage_records",
        "json.dumps(payload",
        "withColumn(\"DQ_STATUS\"",
        "withColumn(\"metadata_table_key\"",
        "spark.createDataFrame(lineage_rows)",
    ]
    for snippet in forbidden_visible_plumbing:
        assert snippet not in code

    assert "from fabricops_kit.pipeline import _write_catalogue_evidence" not in code
    assert "_write_catalogue_evidence(" not in code
    assert code.count("write_catalogue_evidence(") == 2
    assert code.count("write_pipeline_lineage(") == 1


def test_pipeline_notebook_supports_many_sources_and_many_targets_by_definition():
    markdown, code = _notebook_sources()

    assert "SOURCE_DEFINITIONS" not in code
    assert "USE_SAMPLE_DATA" not in code
    assert "DATASET_NAME = \"CHANGE_ME_dataset\"" in code
    assert "Files/sample/minimal_source.csv" not in code
    assert "df_minimal_source = read_lakehouse_table(" in code
    assert "# df_minimal_source = read_lakehouse_csv(CONFIG, ENV_NAME, \"source\", \"Files/CHANGE_ME/source_file.csv\", spark_session=spark, header=True)" in code
    assert "# df_minimal_source = read_warehouse_table(CONFIG, ENV_NAME, \"product\", \"dbo\", \"CHANGE_ME_source_table\", spark_session=spark)" in code
    assert "SOURCE_DATASETS = {" in code
    assert "\"df\": df_minimal_source" in code
    assert "for source_name, source_config in SOURCE_DATASETS.items():" in code
    assert "source_df = source_config[\"df\"]" in code
    assert "source_evidence_definitions" in code
    assert "source_definitions=source_evidence_definitions" in code
    source_registration = code[code.index("SOURCE_DATASETS = {"):code.index("source_evidence_definitions = {")]
    for loader_field in ["kind", "path", "layer", "table_name"]:
        assert loader_field not in source_registration
    assert "SOURCE_DATASETS[\"source_alias\"][\"df\"]" in code

    assert "TARGET_DEFINITIONS" not in code
    assert "TARGET_DATASETS = {" in code
    assert "\"df\": df_minimal_target" in code
    assert "for target_name, target_config in TARGET_DATASETS.items():" in code
    assert "target_df = target_config[\"df\"]" in code
    assert "target_evidence_definitions" in code
    assert "target_definitions=target_evidence_definitions" in code
    assert "target_name" in code
    assert "\"target_name\": \"CHANGE_ME_target_table\"" in code
    assert "target_layer" in code
    assert "\"target_layer\": \"unified\",  # source | unified | product" in code
    assert "Choose the target layer based on where this output should be written" in markdown
    assert "write_mode" in code
    assert (
        code.index("target_profiles = {}")
        < code.index("for target_name, target_config in TARGET_DATASETS.items():", code.index("target_profiles = {}"))
        < code.index("target_catalogue_status = write_catalogue_evidence(\n    target_profiles")
    )
    assert "\ntarget_catalogue_status = write_catalogue_evidence(\n    target_profiles" in code
    audit_alias = code.index("\ndf_minimal_target = TARGET_DATASETS[\"minimal_target\"][\"df\"]", code.index("AUDIT_CREATED_AT"))
    assert (
        code.rindex("for target_name, target_config in TARGET_DATASETS.items():", code.index("AUDIT_CREATED_AT"), audit_alias)
        < audit_alias
    )
    dq_alias = code.index("\ndf_minimal_target = TARGET_DATASETS[\"minimal_target\"][\"df\"]", code.index("target_dq_results = {}"))
    assert (
        code.rindex("for target_name, target_config in TARGET_DATASETS.items():", code.index("target_dq_results = {}"), dq_alias)
        < dq_alias
    )
    assert "Add more sources" in code
    assert "Add more targets" in code
    assert "\"sources\": [" in code
    assert "\"targets\": [" in code
    assert "CHANGE_ME_source_table rows are transformed into CHANGE_ME_target_table" in code
