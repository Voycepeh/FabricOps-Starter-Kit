import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "src" / "fabricops_kit"


def _literal(name: str):
    tree = ast.parse((PKG / "docs_metadata.py").read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        is_annassign = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name
        if (is_assign or is_annassign) and node.value is not None:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in docs_metadata.py")


def _public_modules() -> list[str]:
    rows = _literal("MODULE_DOCS_METADATA")
    return [row["module_name"] for row in rows if row.get("visibility") == "public"]


def _public_symbol_docs() -> set[str]:
    return {row["symbol_name"] for row in _literal("PUBLIC_SYMBOL_DOCS")}


def _package_all() -> set[str]:
    tree = ast.parse((PKG / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
    raise AssertionError("__all__ missing in __init__.py")


def _discover_top_level_public_symbols(module_name: str) -> set[str]:
    module_file = PKG / f"{module_name}.py"
    tree = ast.parse(module_file.read_text(encoding="utf-8"), filename=str(module_file))
    out = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            out.add(node.name)
    return out


MODULE_LOCAL_ALLOWLIST: dict[str, set[str]] = {
    "config": {
        "DatasetContractValidationError",
        "PathConfig",
        "NotebookRuntimeConfig",
        "AIPromptConfig",
        "QualityConfig",
        "GovernanceConfig",
        "ReviewWorkflowConfig",
        "LineageConfig",
        "FrameworkConfig",
        "ConfigSmokeCheckResult",
        "ConfigBootstrapResult",
        "NotebookSetupContext",
        "load_dataset_contract",
        "validate_dataset_contract",
        "assert_valid_dataset_contract",
        "load_and_validate_dataset_contract",
    },
    "data_quality": {"DQEnforcementResult"},
    "fabric_input_output": {"check_naming_convention", "seed_minimal_sample_source_table"},
    "drift": {
        "SchemaDriftError",
        "UnsupportedDataFrameEngineError",
        "detect_dataframe_engine",
        "default_schema_drift_policy",
        "build_schema_snapshot",
        "compare_schema_snapshots",
        "assert_no_blocking_schema_drift",
        "build_and_write_schema_snapshot",
        "load_latest_schema_snapshot",
        "build_and_write_partition_snapshot",
        "load_latest_partition_snapshot",
        "build_drift_evidence_record",
        "prepare_drift_baselines",
        "IncrementalSafetyError",
        "default_incremental_safety_policy",
        "build_partition_snapshot",
        "compare_partition_snapshots",
        "assert_incremental_safe",
        "build_incremental_safety_records",
    },
    "handover": {"build_handover_record"},
    "metadata": {
        "default_evidence_types",
        "build_evidence_row",
        "build_metadata_table_key",
        "build_metadata_column_key",
        "build_dq_rule_key",
        "normalise_records_by_column",
        "column_context_rows_for_spark",
        "write_metadata_rows",
        "write_column_business_context",
        "write_column_governance_context",
    },
}


def test_public_module_top_level_symbols_are_accounted_for():
    docs_symbols = _public_symbol_docs()
    exported_symbols = _package_all()
    violations: list[str] = []

    for module_name in _public_modules():
        discovered = _discover_top_level_public_symbols(module_name)
        module_allowlist = MODULE_LOCAL_ALLOWLIST.get(module_name, set())
        for symbol in sorted(discovered):
            in_docs_and_all = symbol in docs_symbols and symbol in exported_symbols
            allowlisted_module_local = symbol in module_allowlist
            if not (in_docs_and_all or allowlisted_module_local):
                violations.append(
                    f"{module_name}.{symbol} is top-level public but missing from both PUBLIC_SYMBOL_DOCS/__all__ and module allowlist"
                )

    assert not violations, "\n".join(violations)
