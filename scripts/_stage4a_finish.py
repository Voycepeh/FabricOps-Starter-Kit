"""Temporary helper used to complete the Stage 4A Guardrail metadata migration."""

from pathlib import Path


def _replace_block(source: str, container: str, key: str, next_marker: str, replacement: str) -> str:
    container_pos = source.index(container)
    start = source.index(f'    "{key}": {{', container_pos)
    end = source.index(next_marker, start)
    return source[:start] + replacement + source[end:]


def _update_reference_metadata() -> None:
    path = Path("scripts/reference_docs_metadata.py")
    text = path.read_text()

    guardrail_model = '''    "METADATA_GUARDRAIL": {
        "purpose": "Define the expectations the data used in the ETL pipeline should meet.",
        "grain": "One configured Guardrail rule for one Catalogue table or column in one environment.",
        "primary_key": ["guardrail_rule_id"],
        "foreign_keys": [
            {"local_field": "table_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "table_id", "cardinality": "N:1", "statement": "Many Guardrail rules can belong to one logical Catalogue table identity in an environment."},
            {"local_field": "column_id", "referenced_table": "METADATA_DATA_CATALOGUE", "referenced_field": "column_id", "cardinality": "N:1", "statement": "Column-level Guardrail rules reference the Catalogue column through column_id; table-level rules leave column_id empty."},
        ],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Guardrail rule can produce many Guardrail Results across pipeline runs through guardrail_rule_id."},
        ],
    },
'''
    results_model = '''    "METADATA_GUARDRAIL_RESULTS": {
        "purpose": "See whether the expectations of the data in the ETL pipeline run are met.",
        "grain": "One runtime outcome for one Guardrail rule in one pipeline run.",
        "primary_key": ["guardrail_result_id"],
        "foreign_keys": [
            {"local_field": "guardrail_rule_id", "referenced_table": "METADATA_GUARDRAIL", "referenced_field": "guardrail_rule_id", "cardinality": "N:1", "statement": "Many runtime outcomes can come from one configured Guardrail rule."},
        ],
        "relationships": [
            {"cardinality": "1:N", "statement": "One Guardrail Result can have many failed-record Guardrail Row Results through guardrail_result_id."},
        ],
    },
'''
    row_results_model = '''    "METADATA_GUARDRAIL_ROW_RESULTS": {
        "purpose": "See the individual records that failed a Data Quality rule.",
        "grain": "One failed record belonging to one Guardrail Result.",
        "primary_key": ["guardrail_row_result_id"],
        "foreign_keys": [
            {"local_field": "guardrail_result_id", "referenced_table": "METADATA_GUARDRAIL_RESULTS", "referenced_field": "guardrail_result_id", "cardinality": "N:1", "statement": "Many failed records can belong to one Guardrail Result."},
        ],
        "relationships": [],
    },
'''
    text = _replace_block(text, "METADATA_TABLE_MODELS = {", "METADATA_GUARDRAIL", '    "METADATA_GUARDRAIL_RESULTS": {', guardrail_model)
    text = _replace_block(text, "METADATA_TABLE_MODELS = {", "METADATA_GUARDRAIL_RESULTS", '    "METADATA_GUARDRAIL_ROW_RESULTS": {', results_model)
    text = _replace_block(text, "METADATA_TABLE_MODELS = {", "METADATA_GUARDRAIL_ROW_RESULTS", "\n\n}\n\nMETADATA_REFERENCE_ORDER", row_results_model)

    guardrail_owners = '''    "METADATA_GUARDRAIL": {
        "__default__": [
            "fabricops_kit.widgets.widget_author_guardrails.widget_author_guardrails",
            "fabricops_kit.widgets.widget_author_dq_rules.widget_author_dq_rules",
            "fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "configuration_version": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "table_id": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "column_id": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "environment_name": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "guardrail_type": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "rule_id": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "rule_type": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "rule_parameters_json": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "severity": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
        "is_active": ["fabricops_kit.pipeline.guardrail_metadata.canonical_guardrail_rule_record"],
    },
'''
    results_owners = '''    "METADATA_GUARDRAIL_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.check_schema.check_schema",
            "fabricops_kit.pipeline.check_freshness.check_freshness",
            "fabricops_kit.pipeline.check_changes.check_changes",
            "fabricops_kit.pipeline.check_dq.check_dq",
            "fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row",
            "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_result_id": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "run_id": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "environment_name": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "status": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "can_continue": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "severity": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "reason": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "result_payload_json": ["fabricops_kit.pipeline.guardrail_metadata.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
    },
'''
    row_results_owners = '''    "METADATA_GUARDRAIL_ROW_RESULTS": {
        "__default__": [
            "fabricops_kit.pipeline.check_dq.check_dq",
            "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_row_result_id": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "guardrail_result_id": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "row_identity": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "involved_columns_json": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "failed_values_json": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "failure_reason": ["fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
    },
'''
    text = _replace_block(text, "METADATA_COLUMN_OWNERS = {", "METADATA_GUARDRAIL", '    "METADATA_GUARDRAIL_RESULTS": {', guardrail_owners)
    text = _replace_block(text, "METADATA_COLUMN_OWNERS = {", "METADATA_GUARDRAIL_RESULTS", '    "METADATA_GUARDRAIL_ROW_RESULTS": {', results_owners)
    text = _replace_block(text, "METADATA_COLUMN_OWNERS = {", "METADATA_GUARDRAIL_ROW_RESULTS", '    "METADATA_SOURCE_OBSERVATION": {', row_results_owners)
    path.write_text(text)


def _update_runtime_adapter() -> None:
    path = Path("src/fabricops_kit/pipeline/guardrail_metadata.py")
    text = path.read_text()
    replacements = {
        'str(record.get("table_id") or record.get("metadata_table_key") or "")': 'str(record.get("table_id") or "")',
        'str(record.get("column_id") or record.get("metadata_column_key") or "")': 'str(record.get("column_id") or "")',
        '{"metadata_table_key", "partition_value", "change_column", "max_change_value", "observed_at"}': '{"table_id", "partition_value", "change_column", "max_change_value", "observed_at"}',
    }
    for old, new in replacements.items():
        if old not in text:
            raise RuntimeError(f"Expected Stage 4A source text not found: {old}")
        text = text.replace(old, new)
    path.write_text(text)


if __name__ == "__main__":
    _update_reference_metadata()
    _update_runtime_adapter()
