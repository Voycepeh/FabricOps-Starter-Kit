"""Temporary helper used to complete the Stage 4A Guardrail metadata migration."""

from pathlib import Path


def _replace_block(source: str, container: str, key: str, next_marker: str, replacement: str) -> str:
    container_pos = source.index(container)
    start = source.index(f'    "{key}": {{', container_pos)
    end = source.index(next_marker, start)
    return source[:start] + replacement + source[end:]


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected Stage 4A text not found for {label}: {old}")
    return text.replace(old, new, 1)


def _function_block(text: str, name: str) -> tuple[int, int, str]:
    start = text.index(f"def {name}(")
    next_def = text.find("\ndef ", start + 1)
    end = len(text) if next_def < 0 else next_def + 1
    return start, end, text[start:end]


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
            "fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row",
            "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime",
        ],
        "__audit__": ["fabricops_kit.config.audit.build_runtime_audit_fields"],
        "guardrail_result_id": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "guardrail_rule_id": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "run_id": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "environment_name": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "status": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "can_continue": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "severity": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "reason": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
        "result_payload_json": ["fabricops_kit.pipeline.guardrails_shared.write_guardrail_result_row", "fabricops_kit.pipeline.guardrail_metadata.check_dq_runtime"],
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
    text = _replace_once(
        text,
        'from fabricops_kit.config.audit import build_runtime_audit_fields\n',
        'from fabricops_kit.config.audit import build_runtime_audit_fields\n',
        label="guardrail metadata audit import",
    )
    text = _replace_once(
        text,
        '    audit = build_runtime_audit_fields(config=config, env=env)\n    parameters = _parse_parameters(record)\n',
        '    parameters = _parse_parameters(record)\n',
        label="canonical rule audit resolution",
    )
    text = _replace_once(
        text,
        '        "is_active": bool(record.get("is_active", True)),\n        **audit,\n',
        '        "is_active": bool(record.get("is_active", True)),\n',
        label="canonical rule audit fields",
    )
    text = _replace_once(
        text,
        'str(record.get("table_id") or record.get("metadata_table_key") or "")',
        'str(record.get("table_id") or "")',
        label="canonical table id",
    )
    text = _replace_once(
        text,
        'str(record.get("column_id") or record.get("metadata_column_key") or "")',
        'str(record.get("column_id") or "")',
        label="canonical column id",
    )
    text = _replace_once(
        text,
        '{"metadata_table_key", "partition_value", "change_column", "max_change_value", "observed_at"}',
        '{"table_id", "partition_value", "change_column", "max_change_value", "observed_at"}',
        label="observation identity columns",
    )

    writer_start, writer_end, writer_block = _function_block(text, "write_guardrail_result_row")
    shared_path = Path("src/fabricops_kit/pipeline/guardrails_shared.py")
    shared_text = shared_path.read_text()
    shared_start, shared_end, _ = _function_block(shared_text, "write_guardrail_result_row")
    shared_text = shared_text[:shared_start] + writer_block + shared_text[shared_end:]
    shared_path.write_text(shared_text)
    text = text[:writer_start] + "write_guardrail_result_row = runtime.write_guardrail_result_row\n\n" + text[writer_end:]
    path.write_text(text)


def _update_schema_runtime() -> None:
    path = Path("src/fabricops_kit/pipeline/check_schema.py")
    text = path.read_text()
    text = _replace_once(
        text,
        'from fabricops_kit.pipeline.guardrails_shared import stop_if_failed\n',
        'from fabricops_kit.pipeline.guardrails_shared import stop_if_failed, write_guardrail_result_row\n',
        label="shared result writer import",
    )
    text = _replace_once(
        text,
        '    write_guardrail_result_row,\n)\nfrom fabricops_kit.pipeline.guardrails_shared import stop_if_failed, write_guardrail_result_row\n',
        ')\nfrom fabricops_kit.pipeline.guardrails_shared import stop_if_failed, write_guardrail_result_row\n',
        label="remove duplicate writer import",
    )
    text = _replace_once(
        text,
        '    if select_table_guardrail_rule(\n        rules_df, guardrail_type="schema", metadata_table_key=metadata_table_key,\n        environment_name=env,\n    ) is None:\n        raise ValueError(f"No active approved schema rule exists for {metadata_table_key!r}.")\n',
        '    selected_rule = select_table_guardrail_rule(\n        rules_df, guardrail_type="schema", metadata_table_key=metadata_table_key,\n        environment_name=env,\n    )\n    if selected_rule is None:\n        raise ValueError(f"No active approved schema rule exists for {metadata_table_key!r}.")\n',
        label="schema selected rule",
    )
    text = _replace_once(
        text,
        '    if result.get("guardrail_rule_id"):\n',
        '    if selected_rule is not None:\n        result.setdefault("guardrail_rule_id", str(selected_rule.get("guardrail_rule_id") or ""))\n',
        label="schema result persistence",
    )
    path.write_text(text)


def _update_shared_helper_contract() -> None:
    path = Path("tests/contract/test_public_owner_file_pattern.py")
    text = path.read_text()
    text = _replace_once(
        text,
        '    "guardrails_shared.py",\n',
        '    "guardrails_shared.py",\n    "guardrail_metadata.py",\n',
        label="guardrail metadata shared helper",
    )
    path.write_text(text)


def _update_stage4a_tests() -> None:
    path = Path("tests/unit/test_observation_guardrails.py")
    text = path.read_text()
    text = text.replace('"metadata_table_key": "key",', '"table_id": "key",')
    text = text.replace('"activation_state": "active",\n        "review_state": "governance_approved",\n        "rule_key": f"change_{rule_type}_{severity}",', '"is_active": True,\n        "guardrail_rule_id": f"change_{rule_type}_{severity}",\n        "rule_id": f"change_{rule_type}_{severity}",')
    text = text.replace('"activation_state": "active",\n        "review_state": "governance_approved",\n        "rule_key": "freshness_rule",', '"is_active": True,\n        "guardrail_rule_id": "freshness_rule",\n        "rule_id": "freshness_rule",')
    text = text.replace('    rules[0]["review_state"] = "authored"\n', '')
    text = text.replace('rules = [{"rule_key": "schema_rule"}]', 'rules = [{"guardrail_rule_id": "schema_rule", "table_id": "lakehouse||source||dbo||orders", "guardrail_type": "schema", "is_active": True}]', 1)
    text = text.replace('rules = [{"rule_key": "schema_rule"}]', 'rules = [{"guardrail_rule_id": "schema_rule", "table_id": "warehouse||product||sales||orders", "guardrail_type": "schema", "is_active": True}]', 1)
    text = text.replace('return {"status": "passed", "can_continue": True, "rule_key": "schema_rule", "rule_type": "required_columns"}', 'return {"status": "passed", "can_continue": True, "guardrail_rule_id": "schema_rule", "rule_type": "required_columns"}')
    text = text.replace('return {"status": "passed", "can_continue": True, "rule_key": "schema_rule", "rule_type": "strict"}', 'return {"status": "passed", "can_continue": True, "guardrail_rule_id": "schema_rule", "rule_type": "strict"}')
    text = text.replace('result = {"status": "failed", "can_continue": False, "rule_key": "rule", "rule_type": "strict"}', 'result = {"status": "failed", "can_continue": False, "guardrail_rule_id": "rule", "rule_type": "strict", "table_id": "governed-orders", "guardrail_type": "schema", "is_active": True}')
    path.write_text(text)

    path = Path("tests/unit/test_dq_rules.py")
    text = path.read_text()
    old = '{"guardrail_type", "review_status", "source_notebook_type", "superseded_by_rule_key"}'
    new = '{"guardrail_rule_id", "table_id", "column_id", "guardrail_type", "rule_parameters_json", "is_active"}'
    text = _replace_once(text, old, new, label="DQ Stage 4A schema assertion")
    path.write_text(text)

    path = Path("tests/unit/test_guardrail_authoring_model.py")
    text = path.read_text()
    old = '{"approval_required", "approval_bypassed", "requires_post_review", "governance_mode", "approval_policy"}.issubset(rule_fields)'
    new = '{"guardrail_rule_id", "configuration_version", "table_id", "column_id", "guardrail_type", "rule_id", "rule_type", "rule_parameters_json", "severity", "is_active"}.issubset(rule_fields)'
    text = _replace_once(text, old, new, label="Guardrail Stage 4A ownership assertion")
    path.write_text(text)


if __name__ == "__main__":
    _update_reference_metadata()
    _update_runtime_adapter()
    _update_schema_runtime()
    _update_shared_helper_contract()
    _update_stage4a_tests()
