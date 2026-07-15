"""Generate individual function reference pages and reference landing pages."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import UTC, datetime
import html
import json
import sys
import os
from pathlib import Path
import re
import runpy
import subprocess
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generated_artifact_metadata import read_generated_artifact_metadata, update_generated_artifact_metadata
PKG_DIR = ROOT / "src" / "fabricops_kit"
PACKAGE_NAME = "fabricops_kit"
INIT_PATH = PKG_DIR / "__init__.py"
DOCS_METADATA_PATH = ROOT / "scripts" / "reference_docs_metadata.py"
REFERENCE_PATH = ROOT / "docs" / "reference" / "index.md"
REFERENCE_DATA_DIR = ROOT / "docs" / "reference" / "_data"
PUBLIC_CALL_FLOW_DATA_PATH = REFERENCE_DATA_DIR / "public-function-call-flows.json"
MKDOCS_PATH = ROOT / "mkdocs.yml"
CALL_GRAPH_PAGE_PATH = ROOT / "docs" / "reference" / "call-graph.md"
CALLABLE_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
METADATA_REFERENCE_INDEX_PATH = ROOT / "docs" / "reference" / "metadata.md"
METADATA_REFERENCE_DIR = ROOT / "docs" / "reference" / "metadata"
LEGACY_CALLABLE_REFERENCE_DIR = ROOT / "docs" / "reference" / "callables"
INTERNAL_REFERENCE_DIR = ROOT / "docs" / "reference" / "internal"

GITHUB_REPO_URL = "https://github.com/Voycepeh/FabricOps-Starter-Kit"
DEFAULT_SOURCE_REF = "main"
GENERATE_INTERNAL_REFERENCE_PAGES_ENV = "FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES"
CORE_TEMPLATE_KEYS = {"00_env_config", "01_agreement", "02_pipeline", "03_governance", "99_explore"}
AUDIT_FIELD_DESCRIPTIONS = {
    "_committed_by": "User principal or runtime identity that committed the metadata row.",
    "_committed_at": "Timestamp when the metadata row was committed.",
    "_workspace_id": "Fabric workspace identifier captured from runtime audit context.",
    "_workspace_name": "Fabric workspace name captured from runtime audit context.",
    "_notebook_id": "Fabric notebook identifier captured from runtime audit context.",
    "_notebook_name": "Fabric notebook name captured from runtime audit context.",
    "_metadata_lakehouse_name": "Configured metadata lakehouse name used for the write.",
    "_activity_id": "Fabric execution activity identifier for the current notebook or pipeline run.",
}

METADATA_FIELD_DESCRIPTIONS = {
    "agreement_version": "Canonical agreement version associated with the row.",
    "agreement_id": "Stable identifier for the agreement lifecycle.",
    "agreement_name": "Human-readable name for the agreement.",
    "domain": "Business domain recorded for the metadata row.",
    "recipient": "Recipient recorded for the agreement or access context.",
    "provider_steward_id": "Steward identifier recorded for the provider side of the agreement.",
    "recipient_steward_id": "Steward identifier recorded for the recipient side of the agreement.",
    "business_purpose": "Business purpose recorded for the agreement or access request.",
    "steward_id": "Stable identifier for the steward row.",
    "steward_name": "Human-readable steward name.",
    "steward_role": "Configured steward role captured for the row.",
    "contact": "Contact detail captured for the steward record.",
    "effective_from": "Date when the record becomes effective.",
    "effective_to": "Date when the record stops being effective.",
    "is_active": "Whether the row is currently active.",
    "metadata_table_key": (
        "Stable governed data asset key that identifies a table across environment, dataset, "
        "and table context."
    ),
    "metadata_column_key": (
        "Stable governed data asset key that identifies a column across environment, dataset, "
        "table, and column context."
    ),
    "schema_fingerprint": "Deterministic fingerprint for the observed or governed schema snapshot.",
    "environment_name": "Environment name recorded for the metadata row.",
    "store_type": "Configured Fabric store type recorded for the profiled dataset.",
    "layer": "Configured data layer recorded for the profiled dataset.",
    "schema_name": "Lakehouse or warehouse schema name recorded for the dataset when available.",
    "table_name": "Physical table name recorded for the metadata row.",
    "column_name": "Physical column name recorded for the metadata row.",
    "data_type": "Stable data type label recorded for the column.",
    "contract_id": "Stable identifier for the contract row.",
    "contract_version": "Version recorded for the contract row.",
    "contract_status": "Lifecycle status recorded for the contract row.",
    "contract_payload_json": "Serialized contract payload stored for the row.",
    "lineage_event_id": "Deterministic runtime lineage event identifier.",
    "activity_id": "Runtime Fabric activity identifier captured for the lineage row.",
    "notebook_id": "Fabric notebook identifier captured for the lineage row.",
    "notebook_name": "Fabric notebook name captured for the lineage row.",
    "workspace_id": "Fabric workspace identifier captured for the lineage row.",
    "workspace_name": "Fabric workspace name captured for the lineage row.",
    "profile_role": "Whether the profiled dataset participated as a source or target.",
    "profiled_at": "Timestamp when the dataset profile snapshot was captured.",
    "committed_by": "Actor recorded on the lineage row before standard runtime audit fields are appended.",
    "metadata_lakehouse_name": "Configured metadata lakehouse name captured on the lineage row.",
    "user_principal": "User principal recorded for the access row.",
    "role_name": "Role name recorded for the access row.",
    "permission": "Permission recorded for the access row.",
    "access_purpose": "Reason the access row exists.",
    "approval_status": "Approval status recorded for the access row.",
    "access_scope": "Scope of the recorded access entry.",
    "table_id": "Identifier for the accessed table or object.",
    "granted_date": "Date when access was granted.",
    "expires_at": "Timestamp when access expires.",
    "approved_by": "Actor who approved the access row.",
    "approved_at": "Timestamp when the access row was approved.",
    "notes": "Free-text notes recorded for the row.",
    "row_count": "Observed total row count in the profiled dataset snapshot.",
    "non_null_count": "Observed non-null value count for the column.",
    "null_count": "Observed null value count for the column.",
    "null_percent": "Observed null percentage for the column.",
    "distinct_count": "Observed distinct value count for the column.",
    "distinct_percent": "Observed distinct percentage for the column.",
    "mean_value": "Observed mean value for numeric columns when available.",
    "stddev_value": "Observed standard deviation for numeric columns when available.",
    "min_value": "Observed minimum value captured as text.",
    "percentile_25_value": "Observed 25th percentile for numeric columns when available.",
    "median_value": "Observed median value for numeric columns when available.",
    "percentile_75_value": "Observed 75th percentile for numeric columns when available.",
    "max_value": "Observed maximum value captured as text.",
    "is_sampled": "Whether the profiled dataset snapshot was sampled.",
    "frequency_json": "Serialized top-value frequency distribution for the column when requested.",
    "guardrail_rule_id": "Stable identifier for the guardrail rule row.",
    "rule_key": "Stable key used to group lifecycle versions of the same guardrail or enrichment rule.",
    "rule_id": "Rule identity stored by the authoring workflow.",
    "dataset_name": "Dataset name recorded for the metadata row.",
    "guardrail_type": "Guardrail family recorded for the row.",
    "rule_type": "Specific rule type recorded within the guardrail family.",
    "rule_parameters_json": "Serialized rule parameters stored for the guardrail row.",
    "severity": "Severity recorded for the guardrail intent or result.",
    "description": "Human-readable description stored for the rule.",
    "activation_state": "Lifecycle activation state recorded for the row.",
    "review_status": "Review status recorded for the row.",
    "review_state": "Review state recorded for the row.",
    "created_by_role": "Author role recorded for the row.",
    "author_role": "Detailed author role recorded for the guardrail row.",
    "suggestion_json": "Serialized suggested rule payload captured during authoring.",
    "action_type": "Authoring or governance action type recorded for the row.",
    "source_notebook_type": "Notebook type that authored or reviewed the row.",
    "activation_reason": "Human-readable reason for activating the row.",
    "activated_by": "Actor who activated the row.",
    "started_at": "Pipeline bootstrap timestamp captured when the pipeline context is initialized.",
    "completed_at": (
        "Timestamp captured when the pipeline run summary is written. Pipeline duration is derived "
        "from the difference between `started_at` and `completed_at`."
    ),
    "status": "Pipeline run status recorded with the run summary.",
    "submitted_at": "Timestamp populated during a real submission into pending governance review.",
    "reviewed_at": "Timestamp captured when a governance reviewer records a review decision.",
    "reviewed_by": "Actor who recorded the governance review decision.",
    "review_decision": "Governance decision recorded for the row.",
    "review_comment": "Reviewer comment recorded for the row.",
    "activated_at": "Timestamp captured when a rule or enrichment record becomes active.",
    "approval_required": "Whether governance approval is required before activation.",
    "approval_bypassed": "Whether the row bypassed normal governance approval.",
    "requires_governance_review": "Whether the row still requires governance review.",
    "requires_post_review": "Whether the row requires review after immediate activation.",
    "governance_mode": "Governance mode recorded for the selected table.",
    "approval_policy": "Approval policy recorded for the selected table.",
    "submitted_by": "Actor who submitted the row for governance review.",
    "bypassed_at": "Timestamp captured when governance review is intentionally bypassed.",
    "bypassed_by": "Actor who bypassed governance review.",
    "bypass_reason": "Reason recorded when governance review was bypassed.",
    "superseded_by_rule_key": "Rule key that supersedes the current guardrail row.",
    "supersedes_rule_id": "Rule identifier superseded by the current row.",
    "guardrail_result_id": "Stable identifier for the runtime guardrail result row.",
    "result_id": "Stable identifier for the runtime result payload.",
    "reason": "Human-readable runtime reason recorded for the guardrail outcome.",
    "expected_value_json": "Serialized expected value payload for the guardrail outcome.",
    "actual_value_json": "Serialized actual value payload for the guardrail outcome.",
    "result_payload_json": "Serialized full runtime result payload written for the guardrail outcome.",
    "enrichment_rule_id": "Stable identifier for the enrichment rule row.",
    "enrichment_rule_version": "Version recorded for the enrichment rule row.",
    "enrichment_rule_key": "Stable key used to group lifecycle versions of the same enrichment rule.",
    "enrichment_scope": "Whether the enrichment row applies to a table or column.",
    "enrichment_type": "Enrichment type recorded for the row.",
    "enrichment_payload_json": "Serialized enrichment payload stored for the row.",
    "business_name": "Business-friendly name recorded for the table or column.",
    "business_description": "Business description recorded for the table or column.",
    "business_meaning": "Business meaning recorded for the table or column.",
    "column_description": "Column description recorded by the enrichment workflow.",
    "classification": "Classification recorded for the table or column.",
    "sensitivity_label": "Sensitivity label recorded for the table or column.",
    "pii_flag": "Whether the table or column is marked as containing PII.",
    "pii_type": "PII type recorded for the table or column.",
    "data_domain": "Business data domain recorded for the row.",
    "data_owner": "Business owner recorded for the row.",
    "data_steward": "Business steward recorded for the row.",
    "usage_notes": "Usage notes recorded for the row.",
    "quality_notes": "Quality notes recorded for the row.",
    "supersedes_enrichment_rule_id": "Enrichment rule identifier superseded by the current row.",
}
METADATA_RELATED_FUNCTIONS = {
    "METADATA_DATA_AGREEMENT": ["widget_render_data_agreement"],
    "METADATA_DATA_CATALOGUE": ["profile_and_register_dataframe", "widget_enrich_table_metadata"],
    "METADATA_DATA_PROFILED": ["profile_and_register_dataframe", "widget_select_guardrail_target"],
    "METADATA_DATA_LINEAGE": ["profile_and_register_dataframe"],
    "METADATA_DATA_STEWARD": ["widget_render_data_steward"],
    "METADATA_ENRICHMENT": ["widget_enrich_table_metadata", "widget_review_guardrail_governance"],
    "METADATA_GUARDRAIL_RESULTS": ["run_table_guardrails", "display_guardrail_results"],
    "METADATA_GUARDRAIL": [
        "widget_author_schema_freshness_profile_rules",
        "widget_author_dq_rules",
        "widget_review_guardrail_governance",
    ],
}


def _generated_freshness_note() -> list[str]:
    """Return markdown lines describing generated reference freshness."""
    metadata = read_generated_artifact_metadata()
    artifacts = metadata.get("artifacts", {})
    if not isinstance(artifacts, dict):
        artifacts = {}
    reference_pages = artifacts.get("individual_function_reference_pages", {})
    call_flow_data = artifacts.get("public_function_call_flows_json", {})
    reference_generated = reference_pages.get("generated_at_sgt") if isinstance(reference_pages, dict) else None
    data_generated = call_flow_data.get("generated_at_sgt") if isinstance(call_flow_data, dict) else None
    return [
        "",
        "!!! info \"Generated reference freshness\"",
        f"    Reference pages generated: {reference_generated or 'Generated timestamp unavailable'}",
        f"    Call-flow data generated: {data_generated or 'Generated timestamp unavailable'}",
    ]

def plural_word(count: int, singular: str, plural: str) -> str:
    """Return singular or plural text for a count."""
    return singular if count == 1 else plural


def markdown_anchor(value: str) -> str:
    """Return a Material for MkDocs-compatible heading anchor."""
    anchor = re.sub(r"[^a-z0-9 -]", "", value.lower())
    return re.sub(r"[ -]+", "-", anchor).strip("-")


PUBLIC_MODULE_PREFERRED_NAMES = {
    "config.shared": "config",
    "config.get_fabric_context": "config",
    "config.setup_notebook": "config",
    "config.setup_metadata_tables": "config",
    "widgets.widget_select_guardrail_target": "widgets.widget_select_guardrail_target",
    "widgets.widget_author_schema_freshness_profile_rules": "widgets.widget_author_schema_freshness_profile_rules",
    "widgets.widget_author_dq_rules": "widgets.widget_author_dq_rules",
    "widgets.widget_enrich_table_metadata": "widgets.widget_enrich_table_metadata",
    "widgets.widget_review_guardrail_governance": "widgets.widget_review_guardrail_governance",
    "pipeline.profile_dataframe": "pipeline",
    "io": "io",
    "pipeline.guardrails_shared": "pipeline",
    "pipeline": "pipeline",
}
MAJOR_IMPLEMENTATION_MODULE_ORDER = [
    "config",
    "io",
    "pipeline",
]
MAJOR_IMPLEMENTATION_MODULES = set(MAJOR_IMPLEMENTATION_MODULE_ORDER)
INTERNAL_MODULE_BLACKLIST = {"_utils"}
INTERNAL_ALIAS_MODULES = {}

# Callable reference pages are generated from src/fabricops_kit/__init__.py::__all__.
# Keep __all__ as the canonical notebook-facing public callable surface;
# PUBLIC_SYMBOL_DOCS supplies metadata for those exports and may retain extra
# internal helper metadata for relationship details.

# Implementation helper chips should mirror the generated package-local call tree.
# Exclude reachable private helpers only when a callable has an explicit deny
# rule here; this keeps ordinary private implementation helpers visible while
# suppressing intentionally noisy shared plumbing.
INTERNAL_HELPER_EXCLUSIONS: dict[str, set[str]] = {
    "enforce_profile_behavior": {
        "fabricops_kit.io.shared._normalize_schema_name",
        "fabricops_kit.config.shared.get_store",
    },
    "run_table_guardrails": {
        "fabricops_kit.config.shared.get_current_audit_timestamp",
        "fabricops_kit.config.shared.get_audit_timezone",
        "fabricops_kit.config.shared._validate_audit_timezone",
    },
}


SCHEMA_RUNTIME_INTERNAL_HELPERS = {
    f"{PACKAGE_NAME}.pipeline.guardrails_shared._check_schema_runtime",
    f"{PACKAGE_NAME}.pipeline.guardrails_shared._check_schema_rule_runtime",
}


def _is_public_reference_qn(qn: str, node_by_qn: dict[str, dict[str, Any]]) -> bool:
    """Return whether a qualified name should appear in public relationship lists."""
    return bool(node_by_qn.get(qn, {}).get("exported"))


def _hide_from_public_relationships(qn: str) -> bool:
    """Return whether an internal helper should be hidden from public relationship chips."""
    return qn in SCHEMA_RUNTIME_INTERNAL_HELPERS


INTERNAL_HELPER_AUDIT_DECISIONS = {
    "fabricops_kit.config.shared.get_store": "keep_internal",
    "fabricops_kit.config.shared._normalize_path_config": "keep_internal",
    "fabricops_kit.io.shared._normalize_table_name": "keep_internal",
    "fabricops_kit.io.shared._normalize_schema_name": "keep_internal",
    "fabricops_kit.io.shared._resolve_lakehouse_schema": "keep_internal",
    "fabricops_kit.io.shared._resolve_lakehouse_table_path": "keep_internal",
    "fabricops_kit.io.shared.get_spark_session": "keep_internal",
}


PARAMETER_DISPLAY_TYPES = {
    "prepare_pipeline_table_configs": {
        "table_configs": "list[PipelineTableConfig]",
        "default_settings": "Mapping[str, Any] | PipelineTableConfig",
    },
    "run_table_guardrails": {
        "source_definitions": "list[PipelineTableConfig]",
        "target_definitions": "list[PipelineTableConfig]",
    },
    "write_pipeline_run_summary": {
        "source_definitions": "list[PipelineTableConfig]",
        "target_definitions": "list[PipelineTableConfig]",
    },
}

INTERNAL_HELPER_AUDIT_RATIONALE = {
    "keep_internal": "Repeated usage alone is not enough for public utility status; this underscore-prefixed helper exposes implementation plumbing or normalized runtime details rather than a stable user-facing task.",
    "already_covered_by_existing_public_utility": "The direct user-facing need is already covered by an existing public utility, so the helper should stay private.",
    "promote_to_public_utility_candidate": "The helper appears to have stable user-facing behavior, understandable parameters, and return values that can be documented without leaking implementation details.",
}

@dataclass
class Symbol:
    """Symbol metadata container."""

    name: str
    actual_module: str
    public_module: str
    obj_type: str
    summary: str
    role: str = "callable"
    purpose: str = ""


def first_sentence(doc: str | None) -> str:
    """Return the first sentence."""
    if not doc:
        return ""
    line = doc.strip().splitlines()[0].strip()
    return line.split(".")[0].strip() + ("." if "." in line else "")


def _assert_non_placeholder_summary(symbol_name: str, field_name: str, text: str) -> None:
    """Fail fast when placeholder-style summary text is detected."""
    normalized = text.strip()
    if normalized.startswith("Execute the `"):
        raise RuntimeError(f"{symbol_name} has placeholder {field_name}: {normalized}")
    if "Input parameter `" in normalized:
        raise RuntimeError(f"{symbol_name} has placeholder {field_name}: {normalized}")


def _signature_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> str:
    """Return a compact source signature for a function or class."""
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(base) for base in node.bases]
        return f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def _docstring_sections(doc: str | None) -> dict[str, str]:
    """Extract simple NumPy-style docstring sections without changing behavior."""
    if not doc:
        return {}
    lines = doc.strip().splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if line and next_line and set(next_line) <= {"-"} and len(next_line) >= 3:
            current = line.lower().replace(" ", "_")
            sections[current] = []
            index += 2
            continue
        if current is not None:
            sections[current].append(lines[index].rstrip())
        index += 1
    return {key: "\n".join(value).strip() for key, value in sections.items() if "\n".join(value).strip()}


def _docstring_intro(doc: str | None) -> str:
    """Return docstring content that appears before the first NumPy-style section."""
    if not doc:
        return ""
    lines = doc.strip().splitlines()
    intro_lines: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if line and next_line and set(next_line) <= {"-"} and len(next_line) >= 3:
            break
        intro_lines.append(lines[index].rstrip())
        index += 1
    return "\n".join(intro_lines).strip()


def _extended_docstring_intro(doc: str | None) -> str:
    """Return intro content without duplicating the first summary sentence."""
    intro = _docstring_intro(doc)
    if not intro:
        return ""
    summary = first_sentence(doc)
    if not summary:
        return intro
    if intro == summary:
        return ""
    intro_lines = intro.splitlines()
    if intro_lines and intro_lines[0].strip() == summary:
        trimmed = "\n".join(intro_lines[1:]).strip()
        return trimmed
    return intro


def _parameter_doc_metadata(parameters_section: str) -> dict[str, dict[str, str]]:
    """Return first-paragraph NumPy-style parameter docs keyed by parameter name."""
    docs: dict[str, dict[str, Any]] = {}
    current: str | None = None
    for raw_line in parameters_section.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and " : " in line:
            names_part, type_part = stripped.split(" : ", 1)
            names = names_part.split(",")
            current = names[0].strip()
            docs[current] = {"type": type_part.strip(), "description_lines": []}
            continue
        if current is not None:
            docs[current]["description_lines"].append(stripped)
    return {
        name: {"type": str(values.get("type", "")).strip(), "description": " ".join(values.get("description_lines", [])).strip()}
        for name, values in docs.items()
    }


def _clean_parameter_type(type_text: str) -> str:
    """Return a compact parameter type label for definition-list rendering."""
    cleaned = type_text.replace("``", "").strip()
    for suffix in (", optional", ", default=None", ", default = None"):
        cleaned = cleaned.replace(suffix, "")
    return cleaned.strip()


def _parameter_rows_from_node(node: ast.FunctionDef | ast.AsyncFunctionDef, parameters_section: str) -> list[dict[str, str]]:
    """Return compact parameter metadata for generated callable input sections."""
    docs = _parameter_doc_metadata(parameters_section)
    positional = [arg for arg in [*node.args.posonlyargs, *node.args.args] if arg.arg not in {"self", "cls"}]
    positional_required = len(positional) - len(node.args.defaults)
    rows: list[dict[str, str]] = []

    def _row(arg: ast.arg, required: bool) -> dict[str, str]:
        doc = docs.get(arg.arg, {})
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else ""
        return {
            "name": arg.arg,
            "required": "Yes" if required else "No",
            "type": _clean_parameter_type(annotation or doc.get("type", "")),
            "description": doc.get("description", PLACEHOLDER) or PLACEHOLDER,
        }

    for index, arg in enumerate(positional):
        rows.append(_row(arg, index < positional_required))
    for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        rows.append(_row(arg, default is None))
    return rows


def _is_dataclass_class(node: ast.ClassDef) -> bool:
    """Return whether a class node is decorated as a dataclass."""
    return any(
        (isinstance(decorator, ast.Name) and decorator.id == "dataclass")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass")
        or (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Name)
            and decorator.func.id == "dataclass"
        )
        or (
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "dataclass"
        )
        for decorator in node.decorator_list
    )


def _is_property_method(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return whether a function node is decorated as a property accessor."""
    return any(
        (isinstance(decorator, ast.Name) and decorator.id == "property")
        or (isinstance(decorator, ast.Attribute) and decorator.attr == "property")
        for decorator in node.decorator_list
    )


def source_module_name(path: Path) -> str:
    """Return a dotted package-relative source module name."""
    parts = path.relative_to(PKG_DIR).with_suffix("").parts
    if parts[-1] == "__init__":
        return ".".join(parts[:-1])
    return ".".join(parts)


def source_module_paths() -> list[Path]:
    """Return package source files that participate in generated callable metadata."""
    return sorted(path for path in PKG_DIR.rglob("*.py") if path.name != "__init__.py" or path.parent.name in {"pipeline"})


def source_module_path(module: str) -> Path:
    """Return the source path for a dotted package-relative module name."""
    if module == "io":
        return PKG_DIR / "io" / "shared.py"
    if module == "pipeline":
        return PKG_DIR / "pipeline" / "__init__.py"
    if module == "config":
        return PKG_DIR / "config" / "__init__.py"
    return PKG_DIR.joinpath(*module.split(".")).with_suffix(".py")

def parse_module(path: Path) -> dict[str, Any]:
    """Parse module."""
    source_text = path.read_text(encoding="utf-8")
    source_path = path.relative_to(ROOT).as_posix()
    tree = ast.parse(source_text)
    functions: dict[str, str] = {}
    classes: dict[str, str] = {}
    constants: dict[str, str] = {}
    calls: dict[str, set[str]] = {}
    used_by: dict[str, set[str]] = {}
    signatures: dict[str, str] = {}
    doc_sections: dict[str, dict[str, str]] = {}
    source_locations: dict[str, dict[str, int]] = {}
    parameters: dict[str, list[dict[str, str]]] = {}
    doc_intro: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            functions[node.name] = first_sentence(doc)
            signatures[node.name] = _signature_from_node(node)
            sections = _docstring_sections(doc)
            doc_intro[node.name] = _extended_docstring_intro(doc)
            doc_sections[node.name] = sections
            source_locations[node.name] = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
            parameters[node.name] = _parameter_rows_from_node(node, sections.get("parameters", ""))
            called = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        called.add(child.func.id)
                    elif isinstance(child.func, ast.Attribute):
                        called.add(child.func.attr)
            calls[node.name] = called
        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            classes[node.name] = first_sentence(doc)
            signatures[node.name] = _signature_from_node(node)
            sections = _docstring_sections(doc)
            doc_intro[node.name] = _extended_docstring_intro(doc)
            doc_sections[node.name] = sections
            source_locations[node.name] = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
            for child in node.body:
                if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                method_name = f"{node.name}.{child.name}"
                method_doc = ast.get_docstring(child)
                functions[method_name] = first_sentence(method_doc)
                signatures[method_name] = _signature_from_node(child)
                method_sections = _docstring_sections(method_doc)
                doc_intro[method_name] = _extended_docstring_intro(method_doc)
                doc_sections[method_name] = method_sections
                source_locations[method_name] = {
                    "start_line": child.lineno,
                    "end_line": getattr(child, "end_lineno", child.lineno),
                }
                parameters[method_name] = _parameter_rows_from_node(child, method_sections.get("parameters", ""))
                called = set()
                for grandchild in ast.walk(child):
                    if isinstance(grandchild, ast.Call):
                        if isinstance(grandchild.func, ast.Name):
                            called.add(grandchild.func.id)
                        elif isinstance(grandchild.func, ast.Attribute):
                            if isinstance(grandchild.func.value, ast.Name) and grandchild.func.value.id in {"self", "cls"}:
                                called.add(f"{node.name}.{grandchild.func.attr}")
                            else:
                                called.add(grandchild.func.attr)
                calls[method_name] = called
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants[target.id] = ""
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id.isupper():
                constants[target.id] = ""
    names = set(functions) | set(classes)
    for caller, callees in calls.items():
        for callee in names:
            if callee in callees:
                used_by.setdefault(callee, set()).add(caller)
    return {
        "source_path": source_path,
        "functions": functions,
        "classes": classes,
        "constants": constants,
        "calls": calls,
        "used_by": used_by,
        "signatures": signatures,
        "doc_intro": doc_intro,
        "doc_sections": doc_sections,
        "source_locations": source_locations,
        "parameters": parameters,
    }


def parse_import_aliases(nodes: list[ast.stmt]) -> tuple[dict[str, str], dict[str, str]]:
    """Parse import aliases."""
    module_aliases: dict[str, str] = {}
    symbol_aliases: dict[str, str] = {}
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                module_aliases[name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            prefix = "." * node.level
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                if module:
                    symbol_aliases[name] = f"{prefix}{module}.{alias.name}"
                else:
                    module_aliases[name] = f"{prefix}{alias.name}"
    return module_aliases, symbol_aliases


def _callable_expr_name(node: ast.AST) -> str:
    """Return a static callable expression name when it is obvious."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return f"{node.value.id}.{node.attr}"
    return ""


def _collect_dispatch_map_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, set[str]]:
    """Return simple local dispatch-map names keyed to callable object values."""
    dispatch_maps: dict[str, set[str]] = {}
    for child in ast.walk(node):
        if not isinstance(child, (ast.Assign, ast.AnnAssign)) or not isinstance(child.value, ast.Dict):
            continue
        targets = child.targets if isinstance(child, ast.Assign) else [child.target]
        names = [target.id for target in targets if isinstance(target, ast.Name)]
        if not names:
            continue
        values = {_callable_expr_name(value) for value in child.value.values}
        values.discard("")
        if values:
            for name in names:
                dispatch_maps.setdefault(name, set()).update(values)
    return dispatch_maps


def collect_function_calls(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    """Collect function and callable object calls."""
    calls: list[dict[str, str]] = []
    dispatch_maps = _collect_dispatch_map_calls(node)
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        call_target = ""
        call_type = "unknown"
        if isinstance(child.func, ast.Name):
            call_target = child.func.id
            call_type = "name"
        elif isinstance(child.func, ast.Attribute):
            attr = child.func.attr
            if isinstance(child.func.value, ast.Name):
                call_target = f"{child.func.value.id}.{attr}"
            else:
                call_target = attr
            call_type = "attribute"
        elif isinstance(child.func, ast.Subscript) and isinstance(child.func.value, ast.Name):
            for target in sorted(dispatch_maps.get(child.func.value.id, set())):
                calls.append({"raw_name": target, "call_type": "dispatch_map"})
        if call_target:
            calls.append({"raw_name": call_target, "call_type": call_type})
    return calls


def _resolve_relative_import_name(module: str, imported: str) -> str:
    """Resolve a possibly relative import target against a module name."""
    if not imported.startswith("."):
        return imported
    level = len(imported) - len(imported.lstrip("."))
    relative_name = imported[level:]
    module_parts = module.split(".")
    base_parts = module_parts[: max(len(module_parts) - level, 0)]
    return ".".join([*base_parts, relative_name]) if base_parts else relative_name


def resolve_call_target(
    module: str,
    raw_name: str,
    module_aliases: dict[str, str],
    symbol_aliases: dict[str, str],
    same_module_names: set[str],
    exported_symbol_map: dict[str, Symbol],
    package_module_names: set[str],
) -> tuple[str | None, str, str]:
    """Resolve call target."""
    def _classify_callee(module_name: str, symbol_name: str) -> str:
        mapped = exported_symbol_map.get(symbol_name)
        if mapped and mapped.actual_module == module_name:
            return "public_callable" if mapped.role == "callable" else "public_class"
        if symbol_name.startswith("_"):
            return "private_helper"
        return "shared_helper"
    # same-module callable/class names are always safe to resolve first
    if raw_name in same_module_names:
        return f"{PACKAGE_NAME}.{module}.{raw_name}", "same_module", _classify_callee(module, raw_name)

    # explicit import alias from "from x import y as z"
    if raw_name in symbol_aliases:
        imported = _resolve_relative_import_name(module, symbol_aliases[raw_name])
        imported_short = imported.split(".")
        if len(imported_short) >= 2:
            resolved_symbol = imported_short[-1]
            module_candidate = ".".join(imported_short[:-1])
            resolved_module = module_candidate.removeprefix(f"{PACKAGE_NAME}.")
            if imported.startswith(PACKAGE_NAME) or resolved_module in package_module_names:
                exported = exported_symbol_map.get(resolved_symbol)
                target_module = (exported.public_module if exported and exported.actual_module == resolved_module and exported.public_module in {"data_profiling", "pipeline"} else resolved_module)
                callee_kind = _classify_callee(resolved_module, resolved_symbol)
                return (
                    f"{PACKAGE_NAME}.{target_module}.{resolved_symbol}",
                    "cross_module" if resolved_module != module else "same_module",
                    callee_kind,
                )

    # module/alias call like alias.func() or module.func()
    if "." in raw_name:
        owner, member = raw_name.split(".", 1)
        mapped_owner = _resolve_relative_import_name(module, module_aliases.get(owner, owner))
        short_owner = mapped_owner.split(".")[-1]
        resolved_owner = mapped_owner.removeprefix(f"{PACKAGE_NAME}.")
        if mapped_owner.startswith(PACKAGE_NAME) or resolved_owner in package_module_names or short_owner in package_module_names:
            resolved_module = resolved_owner if resolved_owner in package_module_names else short_owner
            exported = exported_symbol_map.get(member)
            target_module = (exported.public_module if exported and exported.actual_module == resolved_module and exported.public_module in {"data_profiling", "pipeline"} else resolved_module)
            callee_kind = _classify_callee(resolved_module, member)
            return f"{PACKAGE_NAME}.{target_module}.{member}", "cross_module" if resolved_module != module else "same_module", callee_kind
        return None, "unresolved", "unresolved"

    # public exported symbol map fallback (bare-name cross-module only for exported mapping)
    exported = exported_symbol_map.get(raw_name)
    if exported and exported.actual_module != module:
        callee_kind = _classify_callee(exported.actual_module, raw_name)
        target_module = exported.public_module if exported.public_module in {"data_profiling", "pipeline"} else exported.actual_module
        return f"{PACKAGE_NAME}.{target_module}.{raw_name}", "cross_module", callee_kind

    return None, "unresolved", "unresolved"


def build_callable_graph(
    module_data: dict[str, dict[str, Any]],
    symbol_map: dict[str, Symbol],
    public_exports: list[str],
    docs_metadata: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build callable graph."""
    package_modules = {m for m in module_data if m not in {"docs_metadata"}}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_keys: set[tuple[str, str]] = set()
    module_summaries: list[dict[str, Any]] = []
    calls_modules: dict[str, set[str]] = {m: set() for m in package_modules}
    called_by_modules: dict[str, set[str]] = {m: set() for m in package_modules}

    def canonical_qualified_name(module: str, callable_name: str) -> str:
        exported = symbol_map.get(callable_name)
        if exported and exported.actual_module == module:
            target_module = exported.public_module if exported.public_module in {"data_profiling", "pipeline"} else exported.actual_module
            return f"{PACKAGE_NAME}.{target_module}.{callable_name}"
        return f"{PACKAGE_NAME}.{module}.{callable_name}"

    for module, info in module_data.items():
        module_tree = ast.parse(source_module_path(module).read_text(encoding="utf-8"))
        module_aliases, symbol_aliases = parse_import_aliases(list(getattr(module_tree, "body", [])))
        functions = info.get("functions", {})
        classes = info.get("classes", {})
        exported_names = {name for name, sym in symbol_map.items() if sym.actual_module == module}
        same_module_names = set(functions) | set(classes)
        dataclass_post_init_methods = {
            f"{class_node.name}.__post_init__"
            for class_node in module_tree.body
            if isinstance(class_node, ast.ClassDef) and _is_dataclass_class(class_node)
            for child in class_node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "__post_init__"
        }
        property_accessor_methods = {
            f"{class_node.name}.{child.name}"
            for class_node in module_tree.body
            if isinstance(class_node, ast.ClassDef)
            for child in class_node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_property_method(child)
        }
        for callable_name in sorted(set(functions) | set(classes)):
            role = str(
                docs_metadata.get(callable_name, {}).get("function_type")
                or "internal"
            ).lower()
            exported = callable_name in exported_names
            if not exported and role not in {"callable", "internal"}:
                role = "internal"
            qualified_name = canonical_qualified_name(module, callable_name)
            key = (module, callable_name)
            if key not in node_keys:
                node_keys.add(key)
                nodes.append(
                    {
                        "callable_name": callable_name,
                        "module_name": module,
                        "qualified_name": qualified_name,
                        "role": role if exported else "internal",
                        "exported": exported,
                        "is_underscore": callable_name.split(".")[-1].startswith("_"),
                        "callable_kind": (
                            "class"
                            if callable_name in classes
                            else "implicit_lifecycle_method"
                            if callable_name in dataclass_post_init_methods
                            else "property_accessor"
                            if callable_name in property_accessor_methods
                            else "callable_object"
                            if callable_name.endswith(".__call__")
                            else "method"
                            if "." in callable_name
                            else "function"
                        ),
                    }
                )

        callable_nodes: list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]] = []
        for node in module_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                callable_nodes.append((node.name, node))
            elif isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        callable_nodes.append((f"{node.name}.{child.name}", child))
        for caller_name, node in callable_nodes:
            caller_qn = canonical_qualified_name(module, caller_name)
            local_module_aliases, local_symbol_aliases = parse_import_aliases(
                [n for n in ast.walk(node) if isinstance(n, (ast.Import, ast.ImportFrom))]
            )
            merged_module_aliases = {**module_aliases, **local_module_aliases}
            merged_symbol_aliases = {**symbol_aliases, **local_symbol_aliases}
            for call in collect_function_calls(node):
                raw_name = call["raw_name"]
                if raw_name.startswith(("self.", "cls.")) and "." in caller_name:
                    raw_name = f"{caller_name.rsplit('.', 1)[0]}.{raw_name.split('.', 1)[1]}"
                resolved_qn, edge_type, callee_kind = resolve_call_target(
                    module, raw_name, merged_module_aliases, merged_symbol_aliases, same_module_names, symbol_map, package_modules
                )
                edge = {
                    "caller_qualified_name": caller_qn,
                    "callee_qualified_name": resolved_qn,
                    "callee_raw_name": raw_name if resolved_qn is None else None,
                    "edge_type": edge_type,
                    "callee_kind": callee_kind,
                }
                edges.append(edge)
                if resolved_qn and edge_type in {"same_module", "cross_module"}:
                    callee_module = resolved_qn.removeprefix(f"{PACKAGE_NAME}.").rsplit(".", 1)[0] if resolved_qn.startswith(f"{PACKAGE_NAME}.") else resolved_qn.split(".")[-2]
                    if callee_module != module:
                        calls_modules[module].add(callee_module)
                        called_by_modules[callee_module].add(module)

        public_count = len([name for name in exported_names if not name.startswith("_")])
        helper_count = len([name for name in functions if name.startswith("_")])
        module_summaries.append(
            {
                "module": module,
                "calls_modules": sorted(calls_modules.get(module, set())),
                "called_by_modules": sorted(called_by_modules.get(module, set())),
                "public_callable_count": public_count,
                "internal_helper_count": helper_count,
            }
        )
    return nodes, edges, sorted(module_summaries, key=lambda x: x["module"])


def parse_public_exports() -> list[str]:
    """Parse public exports."""
    tree = ast.parse(INIT_PATH.read_text(encoding="utf-8"))
    export_groups: dict[str, list[str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        target_names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not target_names:
            continue
        if isinstance(node.value, ast.Tuple):
            values = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
            for target_name in target_names:
                export_groups[target_name] = values
        if "__all__" in target_names and isinstance(node.value, ast.List):
            exports: list[str] = []
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    exports.append(elt.value)
                elif isinstance(elt, ast.Starred) and isinstance(elt.value, ast.Name):
                    exports.extend(export_groups.get(elt.value.id, []))
            if exports:
                return exports
    raise RuntimeError("Could not parse __all__ from __init__.py")


def public_callable_names() -> set[str]:
    """Return notebook-facing public callables from canonical __all__ exports."""
    return set(parse_public_exports())


def parse_docs_metadata() -> dict[str, dict[str, Any]]:
    """Parse docs metadata."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    rows = namespace.get("PUBLIC_SYMBOL_DOCS")
    if not isinstance(rows, list):
        raise RuntimeError("Could not parse PUBLIC_SYMBOL_DOCS from reference_docs_metadata.py")
    seen = set()
    out = {}
    for row in rows:
        name = row["symbol_name"]
        if name in seen:
            raise RuntimeError(f"Duplicate PUBLIC_SYMBOL_DOCS symbol_name detected: {name}")
        seen.add(name)
        out[name] = row
    return out


def parse_usage_note_metadata() -> tuple[dict[str, str], dict[str, str]]:
    """Parse curated usage-note mappings from reference docs metadata."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    path_notes = namespace.get("USAGE_NOTE_BY_PATH_PREFIX", {})
    function_notes = namespace.get("USAGE_NOTE_BY_FUNCTION", {})
    if not isinstance(path_notes, dict) or not isinstance(function_notes, dict):
        raise RuntimeError("Usage-note metadata must be dictionaries")
    return (
        {str(key): str(value).strip() for key, value in path_notes.items()},
        {str(key): str(value).strip() for key, value in function_notes.items()},
    )


def parse_metadata_reference_overview() -> list[str]:
    """Parse curated Metadata Table Overview content from reference docs metadata."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    intro = str(namespace.get("METADATA_REFERENCE_OVERVIEW_INTRO", "")).strip()
    caption = str(namespace.get("METADATA_REFERENCE_MODEL_DIAGRAM_CAPTION", "")).strip()
    diagram = str(namespace.get("METADATA_REFERENCE_MODEL_DIAGRAM", "")).strip()
    if not intro or not caption or not diagram:
        raise RuntimeError("Metadata reference overview content must include intro, caption, and diagram")
    return [intro, "", caption, "", diagram]


def parse_metadata_reference_contract() -> tuple[dict[str, str], dict[str, dict[str, list[Any]]]]:
    """Parse metadata table purpose and column-owner contracts."""
    namespace = runpy.run_path(str(DOCS_METADATA_PATH))
    table_purposes = namespace.get("METADATA_TABLE_PURPOSES", {})
    column_owners = namespace.get("METADATA_COLUMN_OWNERS", {})
    if not isinstance(table_purposes, dict) or not isinstance(column_owners, dict):
        raise RuntimeError("Metadata reference contract must define METADATA_TABLE_PURPOSES and METADATA_COLUMN_OWNERS dictionaries")
    purposes = {str(key): str(value).strip() for key, value in table_purposes.items()}
    normalized_owners: dict[str, dict[str, list[Any]]] = {}
    for table_name, owner_map in column_owners.items():
        if not isinstance(owner_map, dict):
            raise RuntimeError(f"METADATA_COLUMN_OWNERS[{table_name!r}] must be a dictionary")
        normalized_table = {}
        for column_name, owners in owner_map.items():
            if not isinstance(owners, list) or not owners:
                raise RuntimeError(f"METADATA_COLUMN_OWNERS[{table_name!r}][{column_name!r}] must be a non-empty list")
            normalized_table[str(column_name)] = list(owners)
        normalized_owners[str(table_name)] = normalized_table
    return purposes, normalized_owners


def _source_usage_path(source_path: str) -> str:
    """Return package-relative source path used for usage-note prefix matching."""
    return source_path.removeprefix("src/")


def _usage_notes_from_docstring(metadata: dict[str, Any]) -> str:
    """Return fallback usage notes from existing docstring-style metadata."""
    human_use_when = _documented_text(metadata.get("when_to_use"))
    human_do_not_use = _documented_text(metadata.get("do_not_use_when"))
    expanded_purpose = _documented_text(metadata.get("expanded_purpose"))
    usage_guidance_body: list[str] = []
    if human_use_when != PLACEHOLDER:
        usage_guidance_body.extend([human_use_when, ""])
    if human_do_not_use != PLACEHOLDER:
        usage_guidance_body.extend([human_do_not_use, ""])
    if expanded_purpose != PLACEHOLDER:
        usage_guidance_body.extend([expanded_purpose])
    return "\n".join(line for line in usage_guidance_body).strip()


def _usage_notes_for_public_function(
    *,
    function_name: str,
    source_path: str,
    metadata: dict[str, Any],
    usage_note_by_path_prefix: dict[str, str],
    usage_note_by_function: dict[str, str],
) -> str:
    """Return intent-focused Usage notes for a public function page."""
    explicit = _documented_text(metadata.get("usage_notes"))
    if explicit != PLACEHOLDER:
        return explicit
    if function_name in usage_note_by_function:
        return usage_note_by_function[function_name]
    source_usage_path = _source_usage_path(source_path)
    for prefix, note in sorted(usage_note_by_path_prefix.items(), key=lambda item: len(item[0]), reverse=True):
        if source_usage_path.startswith(prefix):
            return note
    return _usage_notes_from_docstring(metadata)


def parse_template_flow_docs() -> list[dict[str, Any]]:
    """Parse template flow docs."""
    tree = ast.parse(DOCS_METADATA_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "TEMPLATE_FLOW_DOCS" for t in node.targets
        )
        is_annassign = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "TEMPLATE_FLOW_DOCS"
        if (is_assign or is_annassign) and node.value is not None:
            return ast.literal_eval(node.value)
    raise RuntimeError("Could not parse TEMPLATE_FLOW_DOCS from reference_docs_metadata.py")


def _render_related_guides(related_guides: list[dict[str, str]]) -> list[str]:
    """Render conceptual documentation links for a callable page."""
    if not related_guides:
        return []

    lines = ["## See also", ""]
    seen: set[tuple[str, str]] = set()
    for guide in related_guides:
        title = str(guide.get("title", "")).strip()
        path = str(guide.get("path", "")).strip()
        if not title or not path:
            raise RuntimeError("related_guides entries must include both title and path")
        key = (title, path)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [{title}]({path})")
    lines.append("")
    return lines


def _metadata_parameter_overrides(value: Any) -> dict[str, str]:
    """Return parameter descriptions supplied by callable metadata."""
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items()}
    return {}


def _markdown_table_cell(text: str) -> str:
    """Escape characters that would otherwise split a Markdown table cell."""
    return text.replace("|", r"\|").replace("\n", "<br>")


def _render_parameter_definitions(parameter_rows: list[dict[str, str]], parameter_overrides: dict[str, str], type_overrides: dict[str, str] | None = None) -> list[str]:
    """Render parameters as a compact API-reference Markdown table."""
    type_overrides = type_overrides or {}
    if not parameter_rows:
        return ["No parameters."]
    lines = ["| Parameter | Type | Required | Description |", "| --- | --- | --- | --- |"]
    for row in parameter_rows:
        name = row["name"]
        required_label = "Yes" if row.get("required") == "Yes" else "No"
        type_text = _markdown_table_cell(type_overrides.get(name, row.get("type", "")).strip() or "—")
        meaning = _markdown_table_cell(parameter_overrides.get(name, row.get("description", PLACEHOLDER)))
        lines.append(f"| `{name}` | `{type_text}` | {required_label} | {meaning} |")
    return lines


def _validate_preferred_example(short_name: str, signature: str, example: str) -> None:
    """Fail when a documented example obviously conflicts with the source signature."""
    if not example.strip():
        return
    try:
        parsed = ast.parse(example)
    except SyntaxError as exc:
        raise RuntimeError(f"{short_name} preferred_example is not valid Python: {exc}") from exc

    calls = [node for node in ast.walk(parsed) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == short_name]
    if not calls:
        return

    keyword_only_match = re.search(rf"def {re.escape(short_name)}\(\*, (?P<body>.*)\)", signature)
    if keyword_only_match is None:
        return

    valid_keyword_names = {
        token.split(":", 1)[0].split("=", 1)[0].strip()
        for token in keyword_only_match.group("body").split(",")
        if token.strip()
    }
    for call in calls:
        if call.args:
            raise RuntimeError(f"{short_name} preferred_example must use keyword arguments for keyword-only parameters.")
        unknown_keywords = {kw.arg for kw in call.keywords if kw.arg is not None} - valid_keyword_names
        if unknown_keywords:
            names = ", ".join(sorted(unknown_keywords))
            raise RuntimeError(f"{short_name} preferred_example uses parameters not in the signature: {names}")


def _render_preferred_example(short_name: str, signature: str, metadata: dict[str, Any]) -> str:
    """Return a validated preferred example for the callable reference page."""
    example = _documented_text(metadata.get("preferred_example"))
    if example != PLACEHOLDER:
        _validate_preferred_example(short_name, signature, example)
    return example


def _render_example_usage(short_name: str, signature: str, metadata: dict[str, Any], doc_examples: str) -> list[str]:
    """Return rendered example usage, preferring docstring Examples content."""
    if doc_examples.strip():
        return _reference_markdown_block(doc_examples, class_name="reference-example-usage")
    preferred_example = _render_preferred_example(short_name, signature, metadata)
    if preferred_example != PLACEHOLDER:
        return _reference_code_block(preferred_example, class_name="reference-example-usage")
    return ["Example usage not documented yet."]

def _read_template_source(template_path: str) -> str:
    """Return searchable source text from a starter notebook/template file."""
    path = ROOT / template_path
    if not path.exists():
        return ""
    if path.suffix == ".ipynb":
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return path.read_text(encoding="utf-8")
        chunks: list[str] = []
        for cell in notebook.get("cells", []):
            source = cell.get("source", "")
            chunks.append("".join(source) if isinstance(source, list) else str(source))
        return "\n".join(chunks)
    return path.read_text(encoding="utf-8")


def _python_source_for_template_analysis(source_text: str) -> str:
    """Return parseable Python source for notebook call analysis."""
    lines: list[str] = []
    for line in source_text.splitlines():
        if line.lstrip().startswith(("%", "!")):
            lines.append(f"# {line}")
        else:
            lines.append(line)
    return "\n".join(lines)


def _direct_public_template_symbols(template_path: str, public_symbols: set[str]) -> list[str]:
    """Return public package callables directly called by a notebook template."""
    path = ROOT / template_path
    if not path.exists():
        return []
    source_text = _read_template_source(template_path)
    if path.suffix == ".ipynb":
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            notebook = {"cells": []}
        code_chunks: list[str] = []
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            source = cell.get("source", "")
            code_chunks.append("".join(source) if isinstance(source, list) else str(source))
        source_text = "\n".join(code_chunks)
    if not source_text:
        return []
    try:
        tree = ast.parse(_python_source_for_template_analysis(source_text))
    except SyntaxError as exc:
        raise RuntimeError(f"Could not parse template for function map validation: {template_path}") from exc

    imported_symbol_by_name: dict[str, str] = {}
    package_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(PACKAGE_NAME):
            for alias in node.names:
                if alias.name in public_symbols:
                    imported_symbol_by_name[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == PACKAGE_NAME:
                    package_aliases.add(alias.asname or alias.name)

    direct_symbols: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in imported_symbol_by_name:
            direct_symbols.add(imported_symbol_by_name[func.id])
        elif (
            isinstance(func, ast.Attribute)
            and func.attr in public_symbols
            and isinstance(func.value, ast.Name)
            and func.value.id in package_aliases
        ):
            direct_symbols.add(func.attr)

    return sorted(direct_symbols)


def _derive_template_usage(
    template_flow_docs: list[dict[str, Any]],
    symbol_map: dict[str, Symbol],
    node_by_qn: dict[str, dict[str, Any]],
    calls_by_qn: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Map public callable names to starter templates that directly call them."""
    del node_by_qn, calls_by_qn
    template_order = {flow["notebook_key"]: index for index, flow in enumerate(template_flow_docs)}
    usage: dict[str, set[str]] = {name: set() for name in symbol_map}

    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        direct_symbols = set(_direct_public_template_symbols(flow.get("template_path", ""), set(symbol_map)))
        for symbol in direct_symbols:
            usage.setdefault(symbol, set()).add(notebook_key)

    return {
        symbol: sorted(notebooks, key=lambda notebook: (template_order.get(notebook, len(template_order)), notebook))
        for symbol, notebooks in usage.items()
    }


def _derive_template_usage_by_kind(
    template_flow_docs: list[dict[str, Any]],
    symbol_map: dict[str, Symbol],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, bool]]:
    """Return direct core calls, example calls, and import-only template usage."""
    template_order = {flow["notebook_key"]: index for index, flow in enumerate(template_flow_docs)}
    core_usage: dict[str, set[str]] = {name: set() for name in symbol_map}
    example_usage: dict[str, set[str]] = {name: set() for name in symbol_map}
    imported_symbols: dict[str, bool] = {name: False for name in symbol_map}
    public_symbols = set(symbol_map)

    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        template_path = flow.get("template_path", "")
        direct_symbols = set(_direct_public_template_symbols(template_path, public_symbols))
        source_text = _read_template_source(template_path)
        for symbol in public_symbols:
            if re.search(rf"\b{re.escape(symbol)}\b", source_text) and symbol not in direct_symbols:
                imported_symbols[symbol] = True
        target = core_usage if notebook_key in CORE_TEMPLATE_KEYS else example_usage
        for symbol in direct_symbols:
            target.setdefault(symbol, set()).add(notebook_key)

    def _sorted_usage(usage: dict[str, set[str]]) -> dict[str, list[str]]:
        return {
            symbol: sorted(notebooks, key=lambda notebook: (template_order.get(notebook, len(template_order)), notebook))
            for symbol, notebooks in usage.items()
        }

    return _sorted_usage(core_usage), _sorted_usage(example_usage), imported_symbols


def generate_internal_reference_pages() -> bool:
    """Return whether standalone internal helper pages should be generated."""
    return os.environ.get(GENERATE_INTERNAL_REFERENCE_PAGES_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def internal_helper_link(actual_module: str, helper: str) -> str:
    """Return module-page-relative link target for an internal helper page."""
    return f"../../reference/internal/{actual_module}_{helper}/"


def public_reference_link(
    symbol: str,
    docs_metadata: dict[str, dict[str, Any]],
    *,
    context: str = "module",
) -> str:
    """Return context-relative link target for a public callable page."""
    if symbol not in docs_metadata:
        raise RuntimeError(f"Missing PUBLIC_SYMBOL_DOCS entry for exported symbol: {symbol}")
    if context == "module":
        return f"../reference/{symbol}/"
    if context == "reference":
        return f"../api/reference/{symbol}/"
    if context == "template_map":
        return f"../api/reference/{symbol}/"
    if context == "notebook":
        return f"../api/reference/{symbol}/"
    raise RuntimeError(f"Unknown link context: {context}")


def callable_docs_link(
    symbol_name: str,
    module: str,
    docs_metadata: dict[str, dict[str, Any]],
    *,
    context: str = "module",
    source_module: str | None = None,
) -> str:
    """Return a safe docs link for a public callable."""
    if symbol_name in docs_metadata and symbol_name in public_callable_names():
        return public_reference_link(symbol_name, docs_metadata, context=context)
    if context == "module":
        if source_module and module != source_module:
            return f"{module}/#{symbol_name}"
        return f"#{symbol_name}"
    if context == "reference":
        return f"#{symbol_name}"
    if context == "notebook":
        return f"#{symbol_name}"
    raise RuntimeError(f"Unknown link context: {context}")


def resolve_preferred_actual_module(preferred_module: str) -> str:
    """Return the likely source module that owns callable implementations."""
    if PUBLIC_MODULE_PREFERRED_NAMES.get(preferred_module) == preferred_module:
        return preferred_module
    return next((actual for actual, public_name in PUBLIC_MODULE_PREFERRED_NAMES.items() if public_name == preferred_module), preferred_module)


def canonical_public_module(module_name: str) -> str:
    """Return the canonical docs/public module name for metadata and manifests."""
    return PUBLIC_MODULE_PREFERRED_NAMES.get(module_name, module_name)


def render_html_table(headers: list[str], rows: list[list[str]], *, table_class: str = "") -> list[str]:
    """Render html table."""
    class_attr = f' class="{table_class}"' if table_class else ""
    lines = [f"<table{class_attr}>", "  <thead>", "    <tr>"]
    for header in headers:
        lines.append(f"      <th>{header}</th>")
    lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
    for row in rows:
        lines.append("    <tr>")
        for idx, cell in enumerate(row):
            label_attr = f' data-label="{html_escape(headers[idx])}"' if table_class in {"reference-template-table", "reference-function-table"} else ""
            lines.append(f"      <td{label_attr}>{cell}</td>")
        lines.append("    </tr>")
    lines.extend(["  </tbody>", "</table>"])
    return lines


def github_source_ref() -> str:
    """Return the stable GitHub ref used by generated source links.

    Generated documentation is published independently from local working trees.
    A local commit SHA can 404 after publishing when it has not been pushed or
    is otherwise unreachable from GitHub, so generated links default to
    ``main``. Release automation may set ``GITHUB_SOURCE_REF`` or
    ``FABRICOPS_SOURCE_REF`` only when it can guarantee the ref is reachable.
    """
    for variable in ("GITHUB_SOURCE_REF", "FABRICOPS_SOURCE_REF"):
        explicit_ref = os.environ.get(variable, "").strip()
        if explicit_ref:
            return explicit_ref
    return DEFAULT_SOURCE_REF


def github_source_url(source_path: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Return a GitHub blob URL for a source file and optional line span."""
    anchor = ""
    if start_line:
        anchor = f"#L{start_line}"
        if end_line and end_line != start_line:
            anchor += f"-L{end_line}"
    return f"{GITHUB_REPO_URL}/blob/{github_source_ref()}/{source_path}{anchor}"


def markdown_details(summary: str, body_lines: list[str], *, class_name: str = "reference-detail") -> list[str]:
    """Render a collapsed Markdown details block."""
    return [f'<details class="{class_name}">', f"<summary>{html_escape(summary)}</summary>", "", *body_lines, "", "</details>"]


def html_escape(text: str) -> str:
    """Escape text for generated inline HTML snippets."""
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def function_chip(name: str, href: str) -> str:
    """Return a clickable function chip for generated docs tables."""
    return f'<a class="function-chip" href="{html_escape(href)}"><code>{html_escape(name)}</code></a>'


def _display_source_path(source_path: str) -> str:
    """Return the package-relative source path used in compact source cards."""
    return source_path.removeprefix("src/")


def _source_card_lines(
    *,
    source_path: str,
    source_start_line: int | None,
    source_ref: str,
    short_name: str,
) -> list[str]:
    """Render a compact source location card with a visible GitHub action."""
    display_path = _display_source_path(source_path)
    line_suffix = f":{source_start_line}" if source_start_line else ""
    return [
        '<div class="reference-source-card" markdown="1">',
        "**Source**",
        "",
        f"`{display_path}{line_suffix}`",
        "",
        f'<a class="reference-source-link" href="{source_ref}">View on GitHub</a>',
        "</div>",
    ]


PLACEHOLDER = "Not documented yet"


def _load_public_call_flow_inventory(path: Path = PUBLIC_CALL_FLOW_DATA_PATH) -> dict[str, Any]:
    """Load the generated public callable inventory used by the dashboard."""
    if not path.exists():
        raise RuntimeError(
            "Missing generated public callable inventory: "
            f"{path.relative_to(ROOT).as_posix()}"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    public_functions = data.get("public_functions")
    if not isinstance(public_functions, list):
        raise RuntimeError("public-function-call-flows.json must contain a public_functions list")
    return data



def _release_source_url(source_path: str, source_ref: str, start_line: int | None = None, end_line: int | None = None) -> str:
    """Return a GitHub source URL pinned to a release ref."""
    anchor = ""
    if start_line:
        anchor = f"#L{start_line}"
        if end_line and end_line != start_line:
            anchor += f"-L{end_line}"
    return f"{GITHUB_REPO_URL}/blob/{source_ref}/{source_path}{anchor}"


def render_function_page_from_record(
    record: dict[str, Any],
    *,
    context: str = "current",
    release_version: str | None = None,
    release_index_href: str = "index.md",
) -> str:
    """Render a public function page from one call-flow contract record."""
    name = str(record["function_name"])
    status = _lifecycle_status(record)
    source_ref = str(record.get("source_ref") or DEFAULT_SOURCE_REF)
    source_url = _release_source_url(
        str(record.get("source_path", "")),
        source_ref,
        record.get("source_start_line"),
        record.get("source_end_line"),
    )
    parameters = record.get("parameters") if isinstance(record.get("parameters"), list) else []
    parameter_lines = _render_parameter_definitions(parameters, {}, {})
    title = f"# `{name}`"
    lines = [title, ""]
    if context == "release":
        if not release_version:
            raise RuntimeError("release_version is required for release page rendering")
        lines.extend([
            f"This page documents `{name}` as released in version `{release_version}`.",
            "",
            f"Release version: `{release_version}`",
            "",
            _lifecycle_chip(status, prominent=True),
            "",
            f"[Current function page](../../../api/reference/{name}.md) · [Release function index]({release_index_href})",
            "",
        ])
    else:
        lines.extend(_lifecycle_header_lines(record))
    lines.extend([
        str(record.get("summary") or "No summary available."),
        "",
        *_source_card_lines(
            source_path=str(record.get("source_path", "")),
            source_start_line=record.get("source_start_line"),
            source_ref=source_url,
            short_name=name,
        ),
        "",
        "## Signature",
        "",
        *_reference_code_block(_format_api_signature(str(record.get("signature") or f"def {name}(...)")), class_name="reference-api-definition"),
        "",
        "## Parameters",
        "",
        *parameter_lines,
        "",
        "## Returns",
        "",
        str(record.get("returns_documentation") or PLACEHOLDER),
        "",
        "## Raises / Errors",
        "",
        str(record.get("raises_documentation") or PLACEHOLDER),
        "",
    ])
    if record.get("examples") and record.get("examples") != PLACEHOLDER:
        lines.extend(["## Example usage", "", *_reference_code_block(str(record["examples"]), class_name="reference-example-usage"), ""])
    if context == "release":
        lines.extend([
            "<details>",
            "<summary>Maintainer architecture details</summary>",
            "",
            f"- Downstream callables: {max(len(record.get('flow', [])) - 1, 0)}",
            f"- Frozen source ref: `{source_ref}`",
            "",
            "</details>",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def generate_release_function_reference_pages(
    *,
    contract_path: Path,
    output_dir: Path,
    release_version: str,
) -> list[Path]:
    """Generate release-specific public function pages from an exact frozen JSON contract."""
    data = _load_public_call_flow_inventory(contract_path)
    rows = sorted(data["public_functions"], key=lambda row: str(row.get("function_name", "")).lower())
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_page in output_dir.glob("*.md"):
        old_page.unlink(missing_ok=True)
    paths: list[Path] = []
    index_lines = [
        f"# Function reference for {release_version}",
        "",
        f"This index lists Live public functions frozen for FabricOps Starter Kit `{release_version}`.",
        "",
        "[Frozen call-flow JSON](../_data/public-function-call-flows.json)",
        "",
        "| Function | Lifecycle | Summary |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        name = str(row["function_name"])
        page_path = output_dir / f"{name}.md"
        page_path.write_text(
            render_function_page_from_record(row, context="release", release_version=release_version),
            encoding="utf-8",
        )
        paths.append(page_path)
        index_lines.append(f"| [`{name}`]({name}.md) | {_lifecycle_chip(_lifecycle_status(row))} | {html_escape(str(row.get('summary') or '—'))} |")
    index_path = output_dir / "index.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return [index_path, *paths]


def _dash(value: Any) -> str:
    """Return a display dash for optional generated-reference values."""
    return "—" if value is None or value == "" else str(value)



def _humanize_contract_value(value: Any) -> str:
    """Return a compact human-readable label for contract enum values."""
    text = _dash(value)
    if text == "—":
        return text
    return text.replace("_", " ").strip().capitalize()


def _lifecycle_status(row: dict[str, Any]) -> str:
    """Return the normalized lifecycle status from the call-flow contract."""
    raw_status = str(row.get("lifecycle_status") or "").strip()
    status = raw_status[:1].upper() + raw_status[1:].lower() if raw_status else ""
    if not status:
        raise RuntimeError(
            "Public function reference lifecycle data missing for:\n"
            f"{row.get('qualified_name', '<unknown>')}"
        )
    return status


def _lifecycle_chip(status: str, label: str | None = None, *, prominent: bool = False) -> str:
    """Return a lifecycle chip using existing reference chip styling hooks."""
    slug = status.lower().replace(" ", "-")
    classes = ["reference-chip", "reference-lifecycle-chip", f"reference-lifecycle-{slug}"]
    if prominent:
        classes.append("reference-lifecycle-chip-prominent")
    return f'<span class="{html_escape(" ".join(classes))}">{html_escape(label or status)}</span>'


def _lifecycle_header_lines(row: dict[str, Any]) -> list[str]:
    """Return lifecycle chips and notice lines for a public callable page."""
    status = _lifecycle_status(row)
    chips = [_lifecycle_chip(status, prominent=True)]
    if status == "Live" and row.get("live_since"):
        chips.append(_lifecycle_chip(status, f"Live since {row['live_since']}", prominent=True))
    if status == "Discontinued" and row.get("discontinued_in"):
        chips.append(_lifecycle_chip(status, f"Discontinued in {row['discontinued_in']}", prominent=True))
    chips.append('<span class="reference-chip reference-chip-muted">Public function</span>')
    notices = {
        "Live": "This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.",
        "Preview": "This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.",
        "Discontinued": "This function is no longer part of the current supported public contract. Use the release history below to identify the last supported version.",
    }
    notice = notices.get(status, f"This function has lifecycle status `{status}` in the public call-flow contract.")
    return [
        '<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">',
        *chips,
        "</p>",
        "",
        f"> {notice}",
        "",
    ]


def _dashboard_link_label(status: str) -> str:
    """Return the lifecycle-aware focused dashboard link label."""
    return {
        "Live": "Open Live contract call flow",
        "Preview": "Open Preview call flow",
        "Discontinued": "Open historical call flow",
    }.get(status, "Open focused call flow")


def _contract_impact_lines(row: dict[str, Any], *, docs_metadata: dict[str, Any], public_page_names: set[str]) -> list[str]:
    """Return the contract-impact section sourced from the call-flow JSON."""
    status = _lifecycle_status(row)
    classification = _humanize_contract_value(row.get("contract_classification"))
    risk = _humanize_contract_value(row.get("contract_risk"))
    lines = [
        "## Contract impact",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| Lifecycle | {_lifecycle_chip(status)} |",
        f"| Live since | {_dash(row.get('live_since'))} |",
        f"| Discontinued in | {_dash(row.get('discontinued_in'))} |",
        f"| Contract classification | {html_escape(str(classification))} |",
        f"| Contract risk | {html_escape(str(risk))} |",
        f"| Live-critical dependencies | {_dash(row.get('live_critical_dependency_count', 0))} |",
        "",
    ]
    history = [item for item in row.get("release_history") or [] if isinstance(item, dict)]
    if history:
        lines.extend(["### Release history", "", "| Status | Version |", "| --- | --- |"])
        for item in history:
            history_status = str(item.get("status") or "").strip().title() or "—"
            version = _dash(item.get("version"))
            lines.append(f"| {html_escape(history_status)} | {html_escape(version)} |")
        lines.append("")

    deps = [str(dep) for dep in row.get("live_critical_dependencies") or []]
    if status == "Live" and deps:
        lines.extend(["### Live-critical dependencies", "", '<ul class="reference-compact-list">'])
        for dep in deps:
            short = dep.rsplit(".", 1)[-1]
            if short in public_page_names:
                href = public_reference_link(short, docs_metadata, context="reference")
                lines.append(f'<li><a href="{html_escape(href)}"><code>{html_escape(dep)}</code></a></li>')
            else:
                lines.append(f'<li><code>{html_escape(dep)}</code></li>')
        lines.extend(["</ul>", ""])
    return lines

def _dashboard_focus_url(function_name: str) -> str:
    """Return the focused dashboard URL for a public function."""
    return f"../../../assets/public-function-call-flows-dashboard.html?function={function_name}"


def _public_callable_docs_url(function_name: str) -> str:
    """Return the docs URL for a public function reference page."""
    return f"../api/reference/{function_name}/"


def _metadata_text(value: Any) -> str:
    """Render metadata values as markdown-friendly text."""
    if value is None or value == "":
        return PLACEHOLDER
    if isinstance(value, dict):
        return "\n".join(f"- `{key}`: {item}" for key, item in value.items()) or PLACEHOLDER
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value) or PLACEHOLDER
    return str(value)


def _documented_text(*values: Any) -> str:
    """Return the first documented text value or a standard placeholder."""
    for value in values:
        text = _metadata_text(value)
        if text != PLACEHOLDER:
            return text
    return PLACEHOLDER


def _code_block(text: str) -> str:
    """Return a fenced Python block for generated reference pages."""
    return f"```python\n{text}\n```"


def _split_top_level_csv(text: str) -> list[str]:
    """Split a comma-separated string while respecting bracketed type expressions."""
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escape = False
    for char in text:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _format_api_signature(signature: str, *, max_inline_length: int = 88) -> str:
    """Return a compact, readable API-definition signature for callable pages."""
    cleaned = signature.strip()
    if not cleaned or len(cleaned) <= max_inline_length or not cleaned.startswith(("def ", "async def ")):
        return cleaned

    match = re.match(r"(?P<prefix>async def|def) (?P<name>\w+)\((?P<body>.*)\)(?P<returns>\s*->\s*.+)?$", cleaned)
    if not match:
        return cleaned

    args = _split_top_level_csv(match.group("body"))
    returns = (match.group("returns") or "").strip()
    rendered_args: list[str] = []
    for arg in args:
        if arg == "*":
            continue
        rendered_args.append(f"    {arg},")
    suffix = f" {returns}" if returns else ""
    return "\n".join([f"{match.group('prefix')} {match.group('name')}(", *rendered_args, f"){suffix}:"])


def _reference_code_block(text: str, *, class_name: str) -> list[str]:
    """Return a styled Markdown-in-HTML code block for callable reference pages."""
    if not text:
        return [PLACEHOLDER]
    return [
        f'<div class="{class_name}" markdown="1">',
        "",
        _code_block(text),
        "",
        "</div>",
    ]


def _reference_markdown_block(text: str, *, class_name: str) -> list[str]:
    """Return a styled Markdown-in-HTML block that preserves rich docstring Markdown."""
    if not text:
        return [PLACEHOLDER]
    return [
        f'<div class="{class_name}" markdown="1">',
        "",
        *text.splitlines(),
        "",
        "</div>",
    ]


def _bullet_lines(text: str) -> list[str]:
    """Return short markdown bullets for human-facing guidance text."""
    cleaned = text.strip()
    if not cleaned:
        return [f"- {PLACEHOLDER}"]
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if len(lines) > 1:
        return [line if line.startswith(("- ", "* ")) else f"- {line}" for line in lines]
    return [cleaned if cleaned.startswith(("- ", "* ")) else f"- {cleaned}"]


def _ai_contract_block(
    *,
    required_context: str,
    inputs: str,
    output: str,
    side_effects: str,
    failure_modes: str,
    verification: str,
) -> str:
    """Render a compact structured implementation contract."""
    return "\n".join(
        [
            f"- **required_context:** {required_context}",
            f"- **inputs:** {inputs}",
            f"- **output:** {output}",
            f"- **side_effects:** {side_effects}",
            f"- **failure_modes:** {failure_modes}",
            f"- **verification:** {verification}",
        ]
    )


def _related_function_links(
    related: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    docs_metadata: dict[str, dict[str, Any]],
) -> list[str]:
    """Render related function links for callable and internal pages."""
    rows: list[str] = []
    for item in related:
        qn = item if item.startswith(f"{PACKAGE_NAME}.") else next(
            (candidate_qn for candidate_qn, candidate_node in node_by_qn.items() if candidate_node["callable_name"] == item),
            item,
        )
        node = node_by_qn.get(qn)
        label = qn
        if node and node.get("exported"):
            href = f"{node['callable_name']}/"
        elif node and generate_internal_reference_pages():
            href = f"../internal/{node['module_name']}_{node['callable_name']}/"
        elif node:
            rows.append(f"- `{label}`")
            continue
        elif item in docs_metadata and item in public_callable_names():
            href = f"../{item}/"
            label = item
        else:
            rows.append(f"- `{label}`")
            continue
        rows.append(f'- <a href="{href}"><code>{label}</code></a>')
    return rows


def _is_internal_helper_qn(qn: str, node_by_qn: dict[str, dict[str, Any]]) -> bool:
    """Return whether a qualified name identifies an internal helper node."""
    node = node_by_qn.get(qn, {})
    return bool(node) and not node.get("exported") and node.get("callable_name", "").startswith("_")


def _collect_internal_helper_descendants(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Return private helper qualified names reachable through the full call tree."""
    seen: set[str] = set()
    helpers: list[str] = []

    def visit(qn: str) -> None:
        for callee in sorted(set(calls_by_qn.get(qn, []))):
            if callee in seen or callee not in node_by_qn:
                continue
            seen.add(callee)
            if _is_internal_helper_qn(callee, node_by_qn):
                helpers.append(callee)
            visit(callee)

    visit(root_qn)
    return helpers


def _callable_flow_internal_helper_qns(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Return sorted internal helper qualified names for callable-flow output."""
    root_name = node_by_qn.get(root_qn, {}).get("callable_name", "")
    excluded_helpers = INTERNAL_HELPER_EXCLUSIONS.get(root_name, set())
    helper_qns = {
        helper_qn
        for helper_qn in _collect_internal_helper_descendants(root_qn, calls_by_qn, node_by_qn)
        if helper_qn not in excluded_helpers
    }
    return sorted(
        helper_qns,
        key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
    )


def _call_tree_link(
    qn: str,
    root_qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> str | None:
    """Return the generated docs or source URL for a call-tree node when available."""
    node = node_by_qn.get(qn)
    if not node:
        return None
    if qn == root_qn:
        return None
    if node.get("exported"):
        return f"../{node['callable_name']}/"
    module_name = node.get("module_name")
    callable_name = node.get("callable_name")
    if module_name and callable_name and module_name in module_data:
        source_location = module_data.get(module_name, {}).get("source_locations", {}).get(callable_name, {})
        return github_source_url(
            f"src/fabricops_kit/{module_name.replace('.', '/')}.py",
            source_location.get("start_line"),
            source_location.get("end_line"),
        )
    return None


def _call_tree_source_prefix(
    qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> str:
    """Return the display source path prefix for a call-tree node."""
    context = context or {}
    source_path = str(context.get("source_path") or context.get("owner_file") or "").strip()
    if source_path:
        return source_path.removeprefix("src/fabricops_kit/")
    module_name = str(context.get("module") or node_by_qn.get(qn, {}).get("module_name") or "").strip()
    return f"{module_name.replace('.', '/')}.py" if module_name else "unknown"


def _call_tree_callable_type(
    qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> str:
    """Return the display callable type suffix for a call-tree node."""
    context = context or {}
    explicit_type = str(
        context.get("function_type")
        or context.get("simple_classification")
        or context.get("layer_group")
        or ""
    ).strip()
    if explicit_type:
        return explicit_type.replace("Public function", "public callable").lower()
    node = node_by_qn.get(qn, {})
    if node.get("exported"):
        return "public callable"
    if node.get("callable_name", "").startswith("_"):
        return "private helper"
    if node.get("callable_kind") in {"class", "method", "property_accessor", "implicit_lifecycle_method"}:
        return str(node.get("callable_kind", "callable")).replace("_", " ")
    return "shared helper"


def _call_tree_label(
    qn: str,
    root_qn: str,
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    recursive: bool = False,
    context: dict[str, Any] | None = None,
) -> str:
    """Render one enriched call-tree callable label, linking package callables when possible."""
    node = node_by_qn.get(qn)
    context = context or {}
    name = context.get("function_name") or context.get("callable") or (node.get("callable_name", qn) if node else qn)
    source_prefix = _call_tree_source_prefix(qn, node_by_qn, context)
    callable_type = _call_tree_callable_type(qn, node_by_qn, context)
    href = _call_tree_link(qn, root_qn, node_by_qn, module_data)
    callable_markup = f"<code>{html_escape(str(name))}(...)</code>"
    if href:
        callable_markup = f'<a href="{html_escape(href)}" class="reference-call-tree-callable">{callable_markup}</a>'
    label = (
        f'<span class="reference-call-tree-source">[{html_escape(source_prefix)}]</span> '
        f'<span class="reference-call-tree-type">[{html_escape(callable_type)}]</span> '
        f"{callable_markup}"
    )
    return label


def _render_clickable_call_tree(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render the full reachable package call tree with recursion protection."""
    lines = [
        '<div class="reference-call-tree" role="tree">',
        f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span>{_call_tree_label(root_qn, root_qn, node_by_qn, module_data)}</div>',
    ]

    def children(qn: str) -> list[str]:
        return sorted(
            {c for c in calls_by_qn.get(qn, []) if c in node_by_qn},
            key=lambda c: (0 if _is_internal_helper_qn(c, node_by_qn) else 1, node_by_qn[c]["callable_name"].lower(), c),
        )

    def visit(qn: str, prefix: str, ancestors: set[str]) -> None:
        child_qns = children(qn)
        for index, child in enumerate(child_qns):
            connector = "└── " if index == len(child_qns) - 1 else "├── "
            recursive = child in ancestors
            lines.append(
                f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">{html_escape(prefix + connector)}</span>{_call_tree_label(child, root_qn, node_by_qn, module_data, recursive=recursive)}</div>'
            )
            if not recursive:
                extension = "    " if index == len(child_qns) - 1 else "│   "
                visit(child, prefix + extension, ancestors | {child})

    visit(root_qn, "", {root_qn})
    lines.append("</div>")
    return lines


def _helper_area_mismatch_signal(helper_name: str, purpose: str, assigned_area: str) -> tuple[str, str, str] | None:
    """Return a wrong-area signal only when name, purpose, and assignment disagree."""
    name_area, _ = _helper_area(helper_name, "")
    purpose_area, _ = _helper_area("", purpose)
    if (
        name_area != "Other"
        and purpose_area != "Other"
        and assigned_area != "Other"
        and len({assigned_area, name_area, purpose_area}) == 3
    ):
        return assigned_area, name_area, purpose_area
    return None


def _callable_identity_keys(value: str | None) -> list[str]:
    """Return dashboard lookup keys for a callable identity."""
    raw = str(value or "").strip()
    if not raw:
        return []
    keys = [raw]
    without_prefix = re.sub(r"^fabricops_kit\.", "", raw)
    keys.append(without_prefix)

    def add(candidate: str | None) -> None:
        if candidate:
            cleaned = re.sub(r"^fabricops_kit\.", "", candidate)
            keys.append(candidate)
            keys.append(f"fabricops_kit.{cleaned}")

    parts = [part for part in without_prefix.split(".") if part]
    last = parts[-1] if parts else ""
    if last:
        keys.append(last)
    if len(parts) >= 2:
        owner = ".".join(parts[:-1])
        keys.append(owner)
        add(owner)
        if parts[-1] == parts[-2]:
            deduped_owner = ".".join(parts[:-1])
            keys.append(deduped_owner)
            add(deduped_owner)
    if len(parts) >= 3:
        module_owner = ".".join(parts[:2])
        module_function = ".".join([*parts[:2], last])
        keys.extend([module_owner, module_function])
        add(module_owner)
        add(module_function)
    return list(dict.fromkeys(key for key in keys if key))


def _public_flow_selection_keys(flow: dict[str, Any]) -> list[str]:
    """Return all dashboard selection keys for a public callable flow."""
    module_name = str(flow.get("module") or "").removeprefix("fabricops_kit.")
    function_name = str(flow.get("function_name") or flow.get("public_callable") or "")
    qualified_name = str(flow.get("qualified_name") or "")
    keys: list[str] = []
    for value in (
        qualified_name,
        function_name,
        module_name,
        f"{module_name}.{function_name}" if module_name and function_name else "",
        f"fabricops_kit.{module_name}.{function_name}" if module_name and function_name else "",
    ):
        keys.extend(_callable_identity_keys(value))
    return list(dict.fromkeys(key for key in keys if key))

def _flow_by_public_qualified_name(callable_flow_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return callable architecture flow records keyed by public qualified name."""
    return {
        flow["qualified_name"]: flow
        for flow in callable_flow_data.get("public_entrypoint_flow", [])
        if flow.get("qualified_name")
    }


def _render_callable_architecture_flow_tree(
    flow: dict[str, Any],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render the same function call graph tree structure used by generated docs."""
    root_qn = flow["qualified_name"]
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for row in flow.get("transitive_callees", []):
        parent_qn = row.get("parent_qualified_name") or root_qn
        by_parent.setdefault(parent_qn, []).append(row)

    lines = [
        '<div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">',
        f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span>{_call_tree_label(root_qn, root_qn, node_by_qn, module_data, context=flow)}</div>',
    ]

    def sort_key(row: dict[str, Any]) -> tuple[int, str, str, str]:
        return (
            int(row.get("depth") or 0),
            str(row.get("module") or ""),
            str(row.get("callable") or "").lower(),
            str(row.get("qualified_name") or ""),
        )

    def visit(parent_qn: str, prefix: str, ancestors: set[str]) -> None:
        child_rows = sorted(by_parent.get(parent_qn, []), key=sort_key)
        for index, child_row in enumerate(child_rows):
            child_qn = child_row.get("qualified_name")
            if not child_qn:
                continue
            connector = "└── " if index == len(child_rows) - 1 else "├── "
            recursive = child_qn in ancestors
            lines.append(
                f'  <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">{html_escape(prefix + connector)}</span>{_call_tree_label(child_qn, root_qn, node_by_qn, module_data, recursive=recursive, context=child_row)}</div>'
            )
            if not recursive:
                extension = "    " if index == len(child_rows) - 1 else "│   "
                visit(child_qn, prefix + extension, ancestors | {child_qn})

    visit(root_qn, "", {root_qn})
    lines.append("</div>")
    return lines


def _collect_refactor_signals(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    excluded_helpers: set[str] | None = None,
) -> dict[str, Any]:
    """Return structured maintainability signals discovered from the full call tree."""
    excluded_helpers = excluded_helpers or set()

    def children(qn: str) -> list[str]:
        return sorted(
            {c for c in calls_by_qn.get(qn, []) if c in node_by_qn},
            key=lambda c: node_by_qn[c]["callable_name"].lower(),
        )

    occurrences: dict[str, int] = {}
    deep_chains: list[list[str]] = []

    def walk(qn: str, path: list[str]) -> None:
        if len(path) > 5:
            deep_chains.append(path)
        for child in children(qn):
            if child not in excluded_helpers:
                occurrences[child] = occurrences.get(child, 0) + 1
            if child not in path:
                walk(child, [*path, child])

    walk(root_qn, [root_qn])

    repeated_helpers = sorted(
        (
            (qn, count)
            for qn, count in occurrences.items()
            if count > 1 and _is_internal_helper_qn(qn, node_by_qn)
        ),
        key=lambda item: (-item[1], node_by_qn[item[0]]["callable_name"].lower()),
    )
    single_delegate_helpers = sorted(
        qn
        for qn in occurrences
        if (
            _is_internal_helper_qn(qn, node_by_qn)
            and len(children(qn)) == 1
            and _is_internal_helper_qn(children(qn)[0], node_by_qn)
        )
    )

    area_mismatch_signals: list[tuple[str, str, str, str, str]] = []
    for qn in occurrences:
        if not _is_internal_helper_qn(qn, node_by_qn):
            continue
        node = node_by_qn[qn]
        module_name = node["module_name"]
        helper_name = node["callable_name"]
        purpose = module_data[module_name].get("functions", {}).get(helper_name) or ""
        assigned_area, _ = _helper_area(helper_name, purpose)
        signal = _helper_area_mismatch_signal(helper_name, purpose, assigned_area)
        if signal:
            name_area: str
            purpose_area: str
            assigned_area, name_area, purpose_area = signal
            area_mismatch_signals.append((helper_name, qn, assigned_area, name_area, purpose_area))

    helper_qns = [
        helper_qn
        for helper_qn in _collect_internal_helper_descendants(root_qn, calls_by_qn, node_by_qn)
        if helper_qn not in excluded_helpers
    ]
    return {
        "qualified_name": root_qn,
        "unique_internal_helper_count": len(helper_qns),
        "repeated_helpers": [
            {
                "helper": node_by_qn[qn]["callable_name"],
                "qualified_name": qn,
                "branch_count": count,
            }
            for qn, count in repeated_helpers[:12]
        ],
        "deep_call_chains": [
            {
                "depth": len(path) - 1,
                "chain": path,
            }
            for path in deep_chains[:8]
        ],
        "single_delegate_helpers": [
            {
                "helper": node_by_qn[qn]["callable_name"],
                "qualified_name": qn,
                "delegates_to": node_by_qn[children(qn)[0]]["callable_name"],
                "delegates_to_qualified_name": children(qn)[0],
            }
            for qn in single_delegate_helpers[:12]
        ],
        "possible_grouping_mismatches": [
            {
                "area": assigned_area,
                "reason": (
                    f"`{helper_name}` is grouped as `{assigned_area}`, but its name suggests "
                    f"`{name_area}` while its summary suggests `{purpose_area}`."
                ),
                "helpers": [
                    {
                        "helper": helper_name,
                        "qualified_name": qn,
                        "name_area": name_area,
                        "purpose_area": purpose_area,
                    }
                ],
            }
            for helper_name, qn, assigned_area, name_area, purpose_area in sorted(
                area_mismatch_signals,
                key=lambda item: (item[2].lower(), item[0].lower()),
            )[:8]
        ],
    }


def _render_refactor_signals(
    signals: dict[str, Any],
    node_by_qn: dict[str, dict[str, Any]],
) -> list[str]:
    """Render structured maintainability signals as human-readable Markdown."""

    def label(qn: str) -> str:
        return node_by_qn[qn]["callable_name"]

    lines = ["### Refactor signals", ""]
    lines.append(
        "These generated hints point maintainers to call-tree shapes worth reviewing; "
        "they are not automatic refactor requirements."
    )
    lines.append("")

    lines.append("**Helpers appearing in multiple branches**")
    lines.append("")
    lines.extend(
        [
            f"- `{item['helper']}` appears in {item['branch_count']} branches."
            for item in signals["repeated_helpers"]
        ]
        or ["- None detected in the reachable package-local call tree."]
    )
    lines.extend(["", "**Call chains deeper than 4 levels**", ""])
    lines.extend(
        [
            f"- {' → '.join(f'`{label(item)}`' for item in chain['chain'])}"
            for chain in signals["deep_call_chains"]
        ]
        or ["- None detected."]
    )
    lines.extend(["", "**Helpers that only call one package-local helper**", ""])
    lines.extend(
        [
            f"- `{item['helper']}` only delegates to `{item['delegates_to']}`."
            for item in signals["single_delegate_helpers"]
        ]
        or ["- None detected."]
    )
    lines.extend(["", "**Helpers grouped into possibly wrong areas**", ""])
    lines.extend(
        [f"- {item['reason']}" for item in signals["possible_grouping_mismatches"]]
        or ["- None detected from helper names, doc summaries, and module placement."]
    )
    return lines


def _reachable_callables(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> set[str]:
    """Return package-local callable qualified names reachable from a root."""
    reachable: set[str] = set()

    def visit(qn: str, ancestors: set[str]) -> None:
        for child in sorted(set(calls_by_qn.get(qn, []))):
            if child not in node_by_qn or child in ancestors:
                continue
            reachable.add(child)
            visit(child, ancestors | {child})

    visit(root_qn, {root_qn})
    return reachable


def _deepest_call_chain_depth(
    root_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> int:
    """Return the deepest package-local call-chain depth below the root."""

    def depth(qn: str, ancestors: set[str]) -> int:
        child_depths = [
            1 + depth(child, ancestors | {child})
            for child in sorted(set(calls_by_qn.get(qn, [])))
            if child in node_by_qn and child not in ancestors
        ]
        return max(child_depths, default=0)

    return depth(root_qn, {root_qn})


def _callable_flow_source_metadata(qn: str, module_data: dict[str, dict[str, Any]]) -> tuple[str | None, str | None, dict[str, int]]:
    """Return module key, callable name, and source location for a function call graph node.

    Public package-level namespaces such as ``fabricops_kit.pipeline`` can
    re-export callables from split implementation owner files. The inventory
    keeps those public qualified names for API surface metadata, but source
    ownership must still resolve to the AST definition file that declares the
    callable.
    """
    parts = qn.split(".")
    package_parts = parts[1:] if parts and parts[0] == PACKAGE_NAME else parts
    for split_at in range(len(package_parts) - 1, 0, -1):
        module_key = ".".join(package_parts[:split_at])
        callable_name = ".".join(package_parts[split_at:])
        source_location = module_data.get(module_key, {}).get("source_locations", {}).get(callable_name)
        if source_location:
            return module_key, callable_name, source_location

    if not package_parts:
        return None, None, {}
    callable_name = package_parts[-1]
    implementation_matches = [
        (module_key, source_locations[callable_name])
        for module_key, info in module_data.items()
        if module_key not in {"docs_metadata"}
        for source_locations in [info.get("source_locations", {})]
        if callable_name in source_locations
    ]
    if len(implementation_matches) == 1:
        module_key, source_location = implementation_matches[0]
        return module_key, callable_name, source_location

    return None, None, {}


def _callable_flow_source_location(qn: str, module_data: dict[str, dict[str, Any]]) -> dict[str, int | None]:
    """Return source line metadata for a function call graph node when available."""
    _, _, source_location = _callable_flow_source_metadata(qn, module_data)
    return {
        "source_start_line": source_location.get("start_line"),
        "source_end_line": source_location.get("end_line"),
    }


def _callable_flow_source_path(qn: str, module_data: dict[str, dict[str, Any]] | None = None) -> str | None:
    """Return the repository source path for a package callable."""
    module_key = None
    if module_data is not None:
        module_key, _, _ = _callable_flow_source_metadata(qn, module_data)
    if module_key is None:
        parts = qn.split(".")
        package_parts = parts[1:] if parts and parts[0] == PACKAGE_NAME else parts
        if len(package_parts) < 2:
            return None
        module_key = ".".join(package_parts[:-1])
    module_info = module_data.get(module_key, {}) if module_data is not None else {}
    source_path = module_info.get("source_path")
    if source_path:
        return source_path
    return f"src/fabricops_kit/{module_key.replace('.', '/')}.py"


def _callable_flow_source_link(qn: str, module_data: dict[str, dict[str, Any]]) -> str | None:
    """Return a source URL for a function call graph node when source metadata exists."""
    _, _, source_location = _callable_flow_source_metadata(qn, module_data)
    if not source_location:
        return None
    source_path = _callable_flow_source_path(qn, module_data)
    if not source_path:
        return None
    return github_source_url(
        source_path,
        source_location.get("start_line"),
        source_location.get("end_line"),
    )


REFACTOR_SIGNAL_ORDER = [
    "Maybe combine",
    "Used several times in one function",
    "Recursive helper",
    "Used by one function",
    "Leaf internal helper",
    "Heavily used helper",
]

REFACTOR_SIGNAL_RECOMMENDATIONS = {
    "Maybe combine": "Maybe combine",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Used by one function": "Used by one function",
    "Leaf internal helper": "Shared utility",
    "Heavily used helper": "Heavily used helper",
}

REFACTOR_REASON_LABELS = {
    "Maybe combine": "Maybe combine",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Used by one function": "Used by one function",
    "Leaf internal helper": "End-of-chain helper",
    "Heavily used helper": "Heavily used helper",
    "public_calls_public": "Public calls public",
    "internal_calls_public": "Internal calls public",
    "internal_workflow_calls_internal_workflow": "Internal workflow calls internal workflow",
    "utility_calls_workflow": "Utility calls workflow",
    "validator_calls_workflow": "Validator calls workflow",
    "resolver_calls_workflow": "Resolver calls workflow",
    "model_calls_workflow": "Model calls workflow",
    "allowed_internal_role_call": "Allowed internal role call",
    "implicit_lifecycle_reachability": "Implicit lifecycle reachability",
    "utility_calls_project_callable": "Utility calls project callable",
    "callee_classification_pending": "Callee classification pending",
    "callee_unreachable": "Callee unreachable",
}

REFACTOR_PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
    "Review": 3,
    "Protect": 4,
}

REFACTOR_PRIORITY_ACTIONS = {
    "Protect": "Shared internal helper",
    "High": "Maybe combine",
    "Medium": "Used by one function",
    "Low": "Shared utility",
    "Review": "Next step",
}

ACTION_LEGEND = {
    "Public API entrypoint": "Supported user-facing API surface; no inbound project calls are required.",
    "Shared internal helper": "Internal implementation helper used by multiple public or internal callers; protect with focused tests before changing.",
    "Shared utility": "Low-level leaf helper with multiple inbound callers; keep generic and project-callable free.",
    "Maybe combine": "This helper is used by one function, and that function uses it once. Review whether keeping it separate makes the code easier to read.",
    "Used by one function": "Helper has one distinct caller. This is a review hint, not an automatic judgment.",
    "Used several times in one function": "This helper is used by one function, but that function uses it more than once. This is usually a reason to keep it, or at least review carefully.",
    "Recursive helper": "Helper calls itself; do not treat it as a simple merge or inline case.",
    "Heavily used helper": "Helper is used by many functions; protect with focused tests before changing.",
    "Next step": "Use the detail text to decide the next architecture action before changing structure.",
    "Broken rule": "Callable dependency direction breaks the public → internal → utility layer rule.",
    "Orphaned callable": "Private callable with no reachable public lineage; remove or reconnect if still needed.",
}


def _project_inbound_callers(
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> dict[str, set[str]]:
    """Return project-local inbound callers for each callable qualified name."""
    inbound: dict[str, set[str]] = {qn: set() for qn in node_by_qn}
    for caller_qn, callees in calls_by_qn.items():
        if caller_qn not in node_by_qn:
            continue
        for callee_qn in set(callees):
            if callee_qn in node_by_qn:
                inbound.setdefault(callee_qn, set()).add(caller_qn)
    return inbound


def _refactor_priority(signals: list[str]) -> str:
    """Return the dashboard priority for an aggregated helper signal list."""
    if "Heavily used helper" in signals:
        return "Protect"
    if "Maybe combine" in signals:
        return "High"
    if "Used several times in one function" in signals or "Recursive helper" in signals or "Used by one function" in signals:
        return "Review"
    if "Leaf internal helper" in signals:
        return "Low"
    return "Low"


def _build_refactor_inventory(
    public_qns: list[str],
    public_class_qns: list[str] | None,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]], list[dict[str, Any]]]:
    """Build one aggregated refactor inventory row per internal helper."""
    inbound_by_qn = _project_inbound_callers(calls_by_qn, node_by_qn)
    signal_index = {name: index for index, name in enumerate(REFACTOR_SIGNAL_ORDER)}
    inventory: list[dict[str, Any]] = []

    def sorted_qns(qns: set[str]) -> list[str]:
        return sorted(
            qns,
            key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()),
        )

    def outbound_project_calls(qn: str) -> list[str]:
        return sorted_qns({callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn})

    def public_lineage(qn: str) -> list[dict[str, str]]:
        lineage: list[dict[str, str]] = []
        for public_qn in public_qns:
            if qn not in _reachable_callables(public_qn, calls_by_qn, node_by_qn):
                continue
            callable_name = node_by_qn[public_qn]["callable_name"]
            lineage.append(
                {
                    "callable": callable_name,
                    "qualified_name": public_qn,
                    "module": node_by_qn[public_qn]["module_name"],
                    "docs_url": _public_callable_docs_url(callable_name),
                }
            )
        return sorted(lineage, key=lambda item: item["callable"].lower())

    def helper_depth(qn: str) -> int | None:
        depths: list[int] = []
        for public_qn in public_qns:
            queue: list[tuple[str, int]] = [(public_qn, 0)]
            seen = {public_qn}
            while queue:
                current_qn, depth = queue.pop(0)
                if current_qn == qn:
                    depths.append(depth)
                    break
                for callee_qn in calls_by_qn.get(current_qn, []):
                    if callee_qn not in node_by_qn or callee_qn in seen:
                        continue
                    seen.add(callee_qn)
                    queue.append((callee_qn, depth + 1))
        return min(depths) if depths else None

    for qn in sorted_qns(set(node_by_qn)):
        if not _is_internal_helper_qn(qn, node_by_qn):
            continue
        inbound = sorted_qns(inbound_by_qn.get(qn, set()))
        outbound = outbound_project_calls(qn)
        inbound_count = len(inbound)
        outbound_count = len(outbound)
        call_site_count = sum(1 for caller in inbound for callee in calls_by_qn.get(caller, []) if callee == qn)
        recursive = qn in calls_by_qn.get(qn, [])
        repeated_within_single_caller = (
            inbound_count == 1 and sum(1 for callee in calls_by_qn.get(inbound[0], []) if callee == qn) > 1
        )
        signals: list[str] = []
        if inbound_count == 1 and call_site_count == 1 and not recursive:
            signals.append("Maybe combine")
        if repeated_within_single_caller:
            signals.append("Used several times in one function")
        if recursive:
            signals.append("Recursive helper")
        if inbound_count == 1:
            signals.append("Used by one function")
        if outbound_count == 0:
            signals.append("Leaf internal helper")
        if inbound_count >= 5:
            signals.append("Heavily used helper")
        signals.sort(key=lambda signal: signal_index[signal])
        priority = _refactor_priority(signals)
        node = node_by_qn[qn]
        inventory.append(
            {
                "function": node["callable_name"],
                "module": node["module_name"],
                "qualified_name": qn,
                "is_internal": True,
                "signals": signals,
                "priority": priority,
                "next_step": REFACTOR_PRIORITY_ACTIONS[priority],
                "recommended_action": REFACTOR_PRIORITY_ACTIONS[priority],
                "inbound_count": inbound_count,
                "call_site_count": call_site_count,
                "recursive": recursive,
                "repeated_within_single_caller": repeated_within_single_caller,
                "outbound_project_call_count": outbound_count,
                "nesting_level": helper_depth(qn),
                "public_entrypoint_lineage": public_lineage(qn),
                "used_by": [
                    {
                        "function": node_by_qn[caller]["callable_name"],
                        "module": node_by_qn[caller]["module_name"],
                        "qualified_name": caller,
                        "source_url": _callable_flow_source_link(caller, module_data),
                    }
                    for caller in inbound
                ],
                "calls": [
                    {
                        "function": node_by_qn[callee]["callable_name"],
                        "module": node_by_qn[callee]["module_name"],
                        "qualified_name": callee,
                        "source_url": _callable_flow_source_link(callee, module_data),
                    }
                    for callee in outbound
                ],
                "source_path": _callable_flow_source_path(qn, module_data),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
            }
        )

    inventory.sort(
        key=lambda row: (REFACTOR_PRIORITY_ORDER[row["priority"]], row["module"], row["function"].lower())
    )
    legacy_signal_rows = [
        {
            "function": row["function"],
            "module": row["module"],
            "qualified_name": row["qualified_name"],
            "is_internal": row["is_internal"],
            "inbound_count": row["inbound_count"],
            "call_site_count": row["call_site_count"],
            "recursive": row["recursive"],
            "repeated_within_single_caller": row["repeated_within_single_caller"],
            "outbound_project_call_count": row["outbound_project_call_count"],
            "signal": signal,
            "recommendation": REFACTOR_SIGNAL_RECOMMENDATIONS[signal],
            "used_by": row["used_by"],
            "calls": row["calls"],
            "source_path": row["source_path"],
            "source_url": row["source_url"],
        }
        for row in inventory
        for signal in row["signals"]
    ]
    legacy_signal_rows.sort(
        key=lambda row: (
            signal_index[row["signal"]],
            row["module"],
            row["function"].lower(),
        )
    )
    summary_counts = {
        "review_for_merge_helpers": sum(1 for row in inventory if "Maybe combine" in row["signals"]),
        "used_by_one_function_helpers": sum(1 for row in inventory if "Used by one function" in row["signals"]),
        "repeated_within_single_caller_helpers": sum(
            1 for row in inventory if "Used several times in one function" in row["signals"]
        ),
        "recursive_helpers": sum(1 for row in inventory if "Recursive helper" in row["signals"]),
        "leaf_internal_helpers": sum(1 for row in inventory if "Leaf internal helper" in row["signals"]),
        "heavily_used_helpers": sum(1 for row in inventory if "Heavily used helper" in row["signals"]),
        "public_api_entrypoints": len(public_qns),
        "internal_helpers": len(inventory),
        "high_priority_candidates": sum(1 for row in inventory if row["priority"] == "High"),
        "medium_priority_candidates": sum(1 for row in inventory if row["priority"] == "Medium"),
        "protect_helpers": sum(1 for row in inventory if row["priority"] == "Protect"),
    }
    return summary_counts, inventory, legacy_signal_rows


CALLABLE_LAYER_LABELS = {
    "public": "Public function",
    "internal": "Shared helper",
}

HIDDEN_PRIVATE_LAYER = "private_helper"
PRIVATE_HELPER_LABEL = "Private helper"
SUPPORTING_OBJECT_LAYER = "supporting_object"
PUBLIC_CLASS_LAYER = "class"
PUBLIC_CLASS_LABEL = "Public config class"

REVIEW_STATUS_LABELS = {
    "classified": "Classified",
    "classification_pending": "Classification pending",
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "unreachable": "Cannot trace back to a public callable",
}

LAYER_CONSISTENCY_LABELS = {
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "matches_layer": "Matches expected layer",
    "questionable_utility": "Questionable utility",
    "promote_to_utility_candidate": "Promote to utility candidate",
    "shared_internal_helper": "Shared internal helper",
    "possible_inline_or_private_helper": "Possible inline/private helper",
    "architecture_violation": "Broken rule",
    "review_manually": "Next step",
}

LAYER_CONSISTENCY_SIGNALS = {
    "implicit_lifecycle": "Implicit lifecycle method",
    "property_accessor": "Property accessor",
    "questionable_utility": "Utility but low reuse",
    "promote_to_utility_candidate": "Promote candidate",
    "shared_internal_helper": "Shared helper",
    "possible_inline_or_private_helper": "Possible inline/private helper",
    "architecture_violation": "Layer assignment needs review",
    "review_manually": "Layer assignment needs review",
}


def _classify_layer_consistency(
    *,
    architecture_layer: str,
    callable_kind: str,
    used_by_count: int,
    calls_count: int,
    has_architecture_violation: bool,
) -> str:
    """Return whether observed call graph usage supports the assigned layer."""
    if callable_kind == "implicit_lifecycle_method":
        return "implicit_lifecycle"
    if callable_kind == "property_accessor":
        return "property_accessor"

    if has_architecture_violation:
        return "architecture_violation"

    if architecture_layer == "Shared helper":
        if used_by_count >= 5:
            return "promote_to_utility_candidate"
        if used_by_count >= 2:
            return "shared_internal_helper"
        if used_by_count <= 1 and callable_kind == "function":
            return "possible_inline_or_private_helper"
        return "matches_layer"

    if architecture_layer == "Public function":
        return "matches_layer"

    return "review_manually"


CONFIG_MODEL_CLASSES = {
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "PathConfig",
}

RESULT_MODEL_CLASSES = {"ConfigSmokeCheckResult"}
CONTEXT_MODEL_CLASSES = {"NotebookSetupContext"}

ROLE_TAGS_BY_NAME = {
    "setup_notebook": ["public_api_entrypoint", "notebook_api_entrypoint", "public_stable"],
    "setup_metadata_tables": ["public_api_entrypoint", "metadata_setup_workflow", "public_stable"],
    "_get_store": ["internal_resolver", "shared_internal_service", "store_resolver", "high_fanout_shared"],
    "resolve_fabric_context": [
        "internal_resolver",
        "shared_internal_service",
        "runtime_context_resolver",
        "high_fanout_shared",
    ],
    "get_default_fabric_context": ["internal_resolver", "runtime_context_provider", "shared_internal_service"],
    "get_current_audit_timestamp": ["audit_time_utility", "shared_internal_service", "high_fanout_shared"],
    "get_audit_timezone": ["internal_resolver", "audit_config_resolver"],
    "build_audit_timestamp_expr": ["audit_time_utility", "spark_audit_expression_utility"],
    "_validate_metadata_table_registration": ["internal_validator", "metadata_table_registration_validator"],
    "_validate_audit_timezone": ["utility_validator", "low_level_utility"],
    "_normalize_path_config": ["internal_normalizer", "path_config_normalizer"],
    "_normalize_widget_config": ["internal_normalizer", "widget_config_normalizer"],
    "_get_metadata_table_schema_registry": ["registry_builder", "metadata_schema_registry_builder"],
    "_metadata_schema_field_names": ["schema_utility"],
    "_string_metadata_schema": ["schema_utility", "local_leaf_helper"],
    "_resolve_metadata_schema": ["internal_resolver", "metadata_schema_resolver"],
    "_get_active_metadata_tables": ["internal_resolver", "metadata_registry_query"],
    "_setup_metadata_table_registry": ["internal_adapter", "metadata_registry_write_adapter"],
    "_detect_nested_metadata_delta_folders": ["internal_validator", "storage_guardrail_validator"],
    "_list_data_stewards": ["internal_resolver", "data_steward_resolver"],
    "widget_render_data_agreement": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_render_data_steward": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_author_dq_rules": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_author_schema_freshness_profile_rules": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_enrich_table_metadata": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_review_guardrail_governance": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "widget_select_guardrail_target": ["public_api_entrypoint", "widget_entrypoint", "public_stable"],
    "_render_agreement_evidence_widget_workflow": ["internal_workflow", "agreement_evidence_widget_workflow"],
    "_latest_metadata_catalogue_lookup_workflow": ["internal_workflow", "metadata_catalogue_lookup_workflow"],
    "_table_metadata_enrichment_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_schema_freshness_profile_rule_authoring_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_dq_rule_authoring_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_guardrail_target_selection_widget_workflow": ["internal_workflow", "widget_workflow"],
    "_guardrail_governance_review_widget_workflow": ["internal_workflow", "widget_workflow"],
    "write_widget_metadata_row": ["internal_adapter", "metadata_write_adapter"],
    "_save_agreement_evidence_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_table_metadata_enrichment_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_enrichment_records": ["internal_adapter", "metadata_write_adapter"],
    "_write_rule_records": ["internal_adapter", "metadata_write_adapter"],
    "_read_metadata_table_or_empty": ["internal_adapter", "metadata_read_adapter"],
    "_read_metadata_rows": ["internal_adapter", "metadata_read_adapter"],
    "_get_governance_metadata_schemas": ["internal_resolver", "governance_metadata_schema_resolver"],
    "_latest_row": ["internal_resolver", "latest_metadata_row_resolver"],
    "_latest_rule": ["internal_resolver", "rule_catalogue_resolver"],
    "_active_steward": ["internal_resolver", "active_steward_resolver"],
    "list_all_data_agreement_rows": ["internal_resolver", "agreement_resolver"],
    "list_data_agreements": ["internal_resolver", "agreement_resolver"],
    "_validate_dq_rules": ["internal_validator", "dq_rule_validator"],
    "_coerce_rows": ["internal_normalizer", "row_payload_normalizer"],
    "_coerce_row_dicts": ["internal_normalizer", "row_payload_normalizer"],
    "_dq_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_schema_freshness_profile_records_from_selection": ["internal_normalizer", "rule_payload_normalizer"],
    "_business_agreement_snapshot": ["internal_normalizer", "agreement_payload_normalizer"],
    "render_searchable_selector": ["internal_adapter", "widget_rendering_adapter"],
    "_selected_catalogue_rows_for_enrichment": ["internal_resolver", "catalogue_table_resolver"],
    "build_enrichment_rule_records": ["internal_normalizer", "rule_payload_normalizer"],
    "_build_metadata_table_key": ["utility_function", "metadata_key_formatter"],
    "apply_governance_enrichment_action": ["internal_normalizer", "rule_payload_normalizer"],
    "apply_governance_rule_action": ["internal_normalizer", "rule_payload_normalizer"],
    "load_rule_review_history": ["internal_resolver", "rule_catalogue_resolver"],

    # Fabric IO public entrypoints and role-organized internals.
    "read_lakehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "write_lakehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_csv": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_parquet": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_excel": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_warehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_warehouse_query": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "write_warehouse_table": ["public_api_entrypoint", "public_stable", "fabric_io_entrypoint"],
    "read_lakehouse_table_core": ["internal_workflow", "io_workflow", "lakehouse_read_workflow"],
    "write_lakehouse_table_core": ["internal_workflow", "io_workflow", "lakehouse_write_workflow"],
    "read_lakehouse_csv_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_lakehouse_parquet_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_lakehouse_excel_core": ["internal_workflow", "io_workflow", "lakehouse_file_read_workflow"],
    "read_warehouse_table_core": ["internal_workflow", "io_workflow", "warehouse_read_workflow"],
    "read_warehouse_query_core": ["internal_workflow", "io_workflow", "warehouse_read_workflow"],
    "write_warehouse_table_core": ["internal_workflow", "io_workflow", "warehouse_write_workflow"],
    "_resolve_target_store": ["internal_resolver", "store_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_schema": ["internal_resolver", "lakehouse_schema_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_table_path": ["internal_resolver", "lakehouse_table_path_resolver", "fabric_io_resolver"],
    "_lakehouse_file_path": ["internal_resolver", "lakehouse_file_path_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_table_location": ["internal_resolver", "lakehouse_table_path_resolver", "fabric_io_resolver"],
    "_resolve_lakehouse_file_location": ["internal_resolver", "lakehouse_file_path_resolver", "fabric_io_resolver"],
    "_resolve_warehouse_table_location": ["internal_resolver", "warehouse_table_resolver", "fabric_io_resolver"],
    "configured_lakehouse_schema": ["internal_resolver", "lakehouse_schema_resolver", "fabric_io_resolver"],
    "_normalize_table_name": ["internal_validator", "name_validator", "fabric_io_validator"],
    "_normalize_schema_name": ["internal_validator", "name_validator", "fabric_io_validator"],
    "_normalize_write_mode": ["internal_validator", "write_mode_validator", "fabric_io_validator"],
    "_validate_lakehouse_store": ["internal_validator", "store_validator", "fabric_io_validator"],
    "_validate_warehouse_store": ["internal_validator", "store_validator", "fabric_io_validator"],
    "_validate_relative_path": ["internal_validator", "file_path_validator", "fabric_io_validator"],
    "_validate_select_query": ["internal_validator", "sql_query_validator", "fabric_io_validator"],
    "_validate_dataframe_writer": ["internal_validator", "dataframe_validator", "fabric_io_validator"],
    "_require_fabric_connector": ["internal_adapter", "fabric_connector_adapter"],
    "_read_delta_path": ["internal_adapter", "spark_read_adapter"],
    "_read_csv_path": ["internal_adapter", "spark_read_adapter"],
    "_write_delta_path": ["internal_adapter", "spark_write_adapter"],
    "_read_warehouse_synapsesql": ["internal_adapter", "fabric_warehouse_adapter"],
    "_write_warehouse_synapsesql": ["internal_adapter", "fabric_warehouse_adapter"],
    "_read_excel_file": ["internal_adapter", "pandas_excel_adapter"],
    "_convert_single_parquet_ns_to_us": ["internal_adapter", "parquet_timestamp_adapter"],
    "_join_lakehouse_area_path": ["utility_function", "path_join_utility"],
    "_build_warehouse_object_name": ["utility_function", "warehouse_name_formatter"],
    "_resolve_lakehouse_table_identifier": ["utility_function", "lakehouse_table_formatter"],

    # Profiling public entrypoint and role-organized internals.
    "profile_dataframe": ["public_api_entrypoint", "profiling_entrypoint", "public_stable"],
    "profile_dataframe_core": ["internal_workflow", "profiling_workflow"],
    "resolve_profiled_columns": ["internal_resolver", "profiling_column_resolver"],
    "is_min_max_supported_type": ["internal_resolver", "spark_type_resolver"],
    "_numeric_bin_edges": ["internal_adapter", "spark_profiling_adapter"],
    "_build_numeric_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "_build_categorical_distribution": ["internal_adapter", "spark_profiling_adapter"],
    "build_distribution_summaries": ["internal_adapter", "spark_profiling_adapter"],

    # Guardrail support internals.
    "_check_schema_rule_runtime": ["internal_workflow", "schema_guardrail_workflow"],
    "_check_schema_runtime": ["internal_validator", "schema_expectation_validator"],
    "enforce_freshness_rule": ["internal_workflow", "freshness_guardrail_workflow"],
    "enforce_freshness": ["internal_workflow", "freshness_guardrail_workflow"],
    "enforce_profile_behavior": ["internal_workflow", "profile_behavior_guardrail_workflow"],
    "_select_table_guardrail_rule": ["internal_resolver", "guardrail_rule_resolver"],
    "_select_profile_behavior_rule": ["internal_resolver", "guardrail_rule_resolver"],
    "_accepted_profile_rows": ["internal_resolver", "profile_baseline_resolver"],
    "_actual_schema": ["internal_resolver", "dataframe_schema_resolver"],
    "_max_column_value": ["internal_adapter", "spark_schema_adapter"],
    "_normalize_datatype": ["internal_normalizer", "schema_result_normalizer"],
    "_normalize_profile": ["internal_normalizer", "profile_payload_normalizer"],
    "_profile_payload_from_profile": ["internal_normalizer", "evidence_payload_normalizer"],
    "_guardrail_exclude_columns": ["internal_resolver", "threshold_config_resolver"],
    "_apply_bypass_post_review_warning": ["internal_normalizer", "guardrail_result_normalizer"],
    "_catalogue_value": ["utility_function", "metadata_value_utility"],
    "_string_value": ["utility_function", "status_message_utility"],
    "_is_active_guardrail_rule": ["internal_validator", "guardrail_rule_validator"],
    "_rule_review_status": ["internal_resolver", "guardrail_rule_resolver"],
    "_parse_rule_parameters": ["internal_resolver", "threshold_config_resolver"],
    "_row_to_dict": ["internal_normalizer", "row_payload_normalizer"],
    "_json_dumps_stable": ["utility_function", "payload_formatter"],
    "_profile_hash": ["utility_function", "payload_hash_utility"],
    "_schema_signature": ["internal_normalizer", "schema_result_normalizer"],
    "_profile_row_count": ["internal_resolver", "profile_payload_resolver"],
    "_coerce_date": ["utility_function", "timestamp_utility"],
    "_iso_date_value": ["utility_function", "timestamp_utility"],
    "_is_missing_table_error": ["utility_function", "error_classification_utility"],
}

REACHABILITY_LABELS = {
    "public_entrypoint": "Public entrypoint",
    "directly_reachable": "Reachable from public API",
    "implicit_lifecycle_reachable": "Lifecycle reachable",
    "unknown_or_entrypoint": "Unknown / possible entrypoint",
    "unreachable_candidate": "Possible unused",
}

ROLE_GROUP_LABELS = {
    "public_entrypoint": "Public entrypoint",
    "workflow": "Workflow",
    "resolver": "Resolver",
    "normalizer": "Normalizer",
    "validator": "Validator",
    "adapter": "Adapter",
    "utility": "Utility",
    "model_class": "Model class",
    "registry_builder": "Registry builder",
    "lifecycle_method": "Lifecycle method",
    "property_method": "Property method",
    "other": "Other",
}


def _callable_role_group(tags: list[str]) -> str:
    """Return the broad role group shown in maintainer dashboard filters."""
    if any(tag in {"public_api_entrypoint", "notebook_api_entrypoint"} for tag in tags):
        return "public_entrypoint"
    if "lifecycle_method" in tags:
        return "lifecycle_method"
    if "property_method" in tags:
        return "property_method"
    if any(tag.endswith("_model_class") or tag == "model_class" for tag in tags):
        return "model_class"
    if any("registry" in tag and ("builder" in tag or "catalog" in tag) for tag in tags):
        return "registry_builder"
    if any("workflow" in tag for tag in tags):
        return "workflow"
    if any("resolver" in tag for tag in tags):
        return "resolver"
    if any("normalizer" in tag for tag in tags):
        return "normalizer"
    if any("validator" in tag for tag in tags):
        return "validator"
    if any("adapter" in tag for tag in tags):
        return "adapter"
    if any("utility" in tag or tag.endswith("_probe") or tag == "shared_internal_service" for tag in tags):
        return "utility"
    return "other"


def _label_from_value(value: str) -> str:
    """Return a compact human-readable label for generated dashboard values."""
    return value.replace("_", " ").strip().capitalize() if value else ""

def _callable_role_tags(
    qn: str,
    node: dict[str, Any],
    layer: str,
    review_status: str,
    *,
    is_called_by_lifecycle: bool = False,
) -> list[str]:
    """Return refined role tags for a callable without changing runtime behavior."""
    name = node["callable_name"]
    base_name = name.split(".")[0]
    kind = node.get("callable_kind", "unknown")
    tags: list[str] = []
    if kind == "implicit_lifecycle_method":
        tags.extend(["lifecycle_method", "implicit_lifecycle_reachable", "keep_lifecycle_method"])
    elif kind == "property_accessor":
        tags.append("property_method")
    elif kind == "class":
        if base_name in CONFIG_MODEL_CLASSES:
            tags.append("config_model_class")
            if base_name == "FrameworkConfig":
                tags.append("root_config_model")
            if base_name == "PathConfig":
                tags.append("path_config_model")
        elif base_name in RESULT_MODEL_CLASSES:
            tags.append("result_model_class")
        elif base_name in CONTEXT_MODEL_CLASSES:
            tags.append("context_model_class")
        else:
            tags.append(
                "config_model_class"
                if base_name.endswith("Config")
                else "context_model_class"
                if base_name.endswith("Context")
                else "result_model_class"
                if base_name.endswith("Result")
                else "instance_method"
            )
    elif layer == "public":
        tags.append("public_api_entrypoint")
    tags.extend(ROLE_TAGS_BY_NAME.get(name, []))
    if not tags:
        if name.startswith("_validate"):
            tags.append("internal_validator")
        elif name.startswith("_normalize"):
            tags.append("internal_normalizer")
        elif name.startswith(("_resolve", "resolve_", "_get", "get_default")):
            tags.append("internal_resolver")
        elif layer == "utility":
            tags.append("utility_function")
        elif layer == "internal":
            tags.append("internal_workflow")
        else:
            tags.append("instance_method" if kind == "method" else "utility_function")
    if is_called_by_lifecycle:
        tags.append("implicit_lifecycle_reachable")
    if review_status == "unreachable":
        tags.append("unreachable_candidate")
    return list(dict.fromkeys(tags))


def _primary_dependency_role(tags: list[str]) -> str:
    """Return the primary dependency role used by architecture rules."""
    order = [
        "public_api_entrypoint",
        "notebook_api_entrypoint",
        "internal_workflow",
        "utility_function",
        "utility_validator",
        "internal_validator",
        "internal_normalizer",
        "internal_resolver",
        "internal_adapter",
        "config_model_class",
        "result_model_class",
        "context_model_class",
        "lifecycle_method",
        "schema_utility",
        "audit_time_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
        "shared_internal_service",
    ]
    return next((role for role in order if role in tags), tags[0] if tags else "unknown")


def _role_dependency_signals(caller_role: str, callee_role: str) -> list[str]:
    """Return role-based architecture signals for a project-local call edge."""
    if caller_role == "internal_workflow" and callee_role == "internal_workflow":
        return ["internal_workflow_calls_internal_workflow"]
    utility_roles = {
        "utility_function",
        "audit_time_utility",
        "schema_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
    }
    if caller_role in utility_roles and callee_role == "internal_workflow":
        return ["utility_calls_workflow"]
    if caller_role in {"utility_validator", "internal_validator"} and callee_role == "internal_workflow":
        return ["validator_calls_workflow"]
    if caller_role == "internal_resolver" and callee_role == "internal_workflow":
        return ["resolver_calls_workflow"]
    if caller_role in {"config_model_class", "result_model_class", "context_model_class"} and callee_role == "internal_workflow":
        return ["model_calls_workflow"]
    allowed_callers = {"public_api_entrypoint", "notebook_api_entrypoint", "internal_workflow", "lifecycle_method"}
    allowed_callees = {
        "internal_workflow",
        "utility_function",
        "utility_validator",
        "internal_validator",
        "internal_normalizer",
        "internal_resolver",
        "internal_adapter",
        "config_model_class",
        "result_model_class",
        "context_model_class",
        "schema_utility",
        "audit_time_utility",
        "spark_runtime_probe",
        "fabric_runtime_probe",
    }
    if caller_role in allowed_callers and callee_role in allowed_callees:
        return ["allowed_internal_role_call"]
    return []

ARCHITECTURE_VIOLATION_ACTION = "Broken rule"


def _callable_classification(
    qn: str,
    public_qn_set: set[str],
    public_class_qn_set: set[str],
    reachable_non_public: set[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    """Return architecture layer and review status for a project callable."""
    node = node_by_qn[qn]
    if node.get("callable_kind") != "function":
        if qn in public_class_qn_set:
            return PUBLIC_CLASS_LAYER, "classified"
        return SUPPORTING_OBJECT_LAYER, "classified"
    if node.get("is_underscore"):
        return HIDDEN_PRIVATE_LAYER, "classified"
    if qn in public_qn_set:
        return "public", "classified"
    layer = "internal"
    if qn not in reachable_non_public:
        review_status = "unreachable" if node.get("is_underscore") else "classification_pending"
        return layer, review_status
    return layer, "classified"


def _architecture_dependency_signals(caller_layer: str, callee_layer: str) -> list[str]:
    """Return callable-layer dependency violation signals for a classified project-local edge."""
    if caller_layer == "public" and callee_layer == "public":
        return ["public_calls_public"]
    if caller_layer == "internal" and callee_layer == "public":
        return ["internal_calls_public"]
    return []


def _dependency_review_signals(callee_review_status: str) -> list[str]:
    """Return review-only signals for edges into pending or unreachable callables."""
    if callee_review_status == "classification_pending":
        return ["callee_classification_pending"]
    if callee_review_status == "unreachable":
        return ["callee_unreachable"]
    return []


def _build_function_inventory(
    public_qns: list[str],
    public_class_qns: list[str] | None,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    callable_summary: list[dict[str, Any]],
    refactor_inventory: list[dict[str, Any]],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    """Build a reconciled one-row-per-discovered-callable dashboard inventory."""
    public_qn_set = set(public_qns)
    public_class_qn_set = set(public_class_qns or [])
    reachable_non_public = set().union(
        *(_reachable_callables(public_qn, calls_by_qn, node_by_qn) for public_qn in public_qns)
    ) - public_qn_set
    inbound_by_qn = _project_inbound_callers(calls_by_qn, node_by_qn)
    refactor_by_qn = {row["qualified_name"]: row for row in refactor_inventory}
    summary_by_qn = {row["qualified_name"]: row for row in callable_summary}
    classification_by_qn = {
        qn: _callable_classification(qn, public_qn_set, public_class_qn_set, reachable_non_public, calls_by_qn, node_by_qn)
        for qn in node_by_qn
    }
    for qn, callers in inbound_by_qn.items():
        if classification_by_qn[qn][1] == "unreachable" and any(
            node_by_qn[caller].get("callable_kind") == "implicit_lifecycle_method" for caller in callers
        ):
            classification_by_qn[qn] = (classification_by_qn[qn][0], "classified")
    layer_by_qn = {qn: classification[0] for qn, classification in classification_by_qn.items()}
    review_status_by_qn = {qn: classification[1] for qn, classification in classification_by_qn.items()}

    def is_visible_architecture_function(qn: str) -> bool:
        return layer_by_qn.get(qn) in {"public", "internal"}

    runtime_reachable_qns = public_qn_set | public_class_qn_set | reachable_non_public

    def is_inventory_function(qn: str) -> bool:
        layer = layer_by_qn.get(qn)
        return layer in {"public", "internal", HIDDEN_PRIVATE_LAYER, PUBLIC_CLASS_LAYER}

    def inventory_function_type(layer: str) -> str:
        if layer == HIDDEN_PRIVATE_LAYER:
            return PRIVATE_HELPER_LABEL
        if layer == PUBLIC_CLASS_LAYER:
            return PUBLIC_CLASS_LABEL
        return CALLABLE_LAYER_LABELS[layer]

    def private_helper_usage_scope(qn: str, inbound: set[str]) -> str:
        if not inbound:
            return "unused"
        helper_module = node_by_qn[qn]["module_name"]
        inbound_modules = {node_by_qn[caller]["module_name"] for caller in inbound if caller in node_by_qn}
        return "same_module" if inbound_modules <= {helper_module} else "cross_module"

    def private_helper_owner(qn: str, inbound: set[str]) -> str:
        visible_callers = [caller for caller in inbound if is_visible_architecture_function(caller)]
        candidates = visible_callers or [caller for caller in inbound if caller in node_by_qn]
        if not candidates:
            return ""
        return sorted(candidates, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()))[0]

    def private_helper_action(qn: str, inbound: set[str], outbound: list[str]) -> tuple[str, str]:
        scope = private_helper_usage_scope(qn, inbound)
        if node_by_qn[qn]["module_name"] == "pipeline.shared":
            return "Keep private helper", "Low"
        if scope == "cross_module":
            return "Rename to shared helper", "Medium"
        if not inbound:
            return "Remove redundant wrapper", "Medium"
        if len(inbound) == 1 and len(set(outbound)) <= 1:
            return "Merge into owner", "Medium"
        if len(inbound) == 1 and node_by_qn[qn]["module_name"] not in {node_by_qn[caller]["module_name"] for caller in inbound}:
            return "Move closer to owner", "Medium"
        return "Keep private helper", "Low"

    lifecycle_called_qns = {
        qn
        for qn, callers in inbound_by_qn.items()
        if any(node_by_qn[caller].get("callable_kind") == "implicit_lifecycle_method" for caller in callers)
    }
    role_tags_by_qn = {
        qn: _callable_role_tags(
            qn,
            node_by_qn[qn],
            layer_by_qn[qn],
            review_status_by_qn[qn],
            is_called_by_lifecycle=qn in lifecycle_called_qns,
        )
        for qn in node_by_qn
    }
    dependency_role_by_qn = {qn: _primary_dependency_role(tags) for qn, tags in role_tags_by_qn.items()}

    def linked(qns: list[str] | set[str]) -> list[dict[str, str]]:
        return [
            {
                "function": node_by_qn[qn]["callable_name"],
                "module": node_by_qn[qn]["module_name"],
                "qualified_name": qn,
                "source_url": _callable_flow_source_link(qn, module_data),
                **(
                    {
                        "docs_path": f"docs/api/reference/{node_by_qn[qn]['callable_name']}.md",
                        "docs_url": _public_callable_docs_url(node_by_qn[qn]["callable_name"]),
                    }
                    if qn in public_qn_set
                    else {}
                ),
                "layer": layer_by_qn.get(qn, "internal"),
                "review_status": review_status_by_qn.get(qn, "classification_pending"),
                "callable_kind": node_by_qn[qn].get("callable_kind", "unknown"),
                "callable_role": role_tags_by_qn.get(qn, []),
                "dependency_role": dependency_role_by_qn.get(qn, "unknown"),
            }
            for qn in sorted(qns, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower()))
            if qn in node_by_qn and is_inventory_function(qn)
        ]

    inventory: list[dict[str, Any]] = []
    for qn in sorted(node_by_qn, key=lambda item: (node_by_qn[item]["module_name"], node_by_qn[item]["callable_name"].lower(), item)):
        if not is_inventory_function(qn):
            continue
        node = node_by_qn[qn]
        layer = layer_by_qn[qn]
        function_type = inventory_function_type(layer)
        refactor = refactor_by_qn.get(qn, {})
        public_summary = summary_by_qn.get(qn, {})
        outbound = [callee for callee in calls_by_qn.get(qn, []) if callee in node_by_qn]
        inbound = inbound_by_qn.get(qn, set())
        direct_helper_qns = {item["qualified_name"] for item in public_summary.get("direct_internal_helpers", [])}
        review_status = review_status_by_qn[qn]
        callable_kind = node.get("callable_kind", "unknown")
        architecture_signals = sorted({
            signal
            for callee in outbound
            if is_visible_architecture_function(qn)
            and is_visible_architecture_function(callee)
            and review_status_by_qn.get(callee, "classification_pending") == "classified"
            for signal in _architecture_dependency_signals(layer, layer_by_qn.get(callee, "internal"))
        })
        allowed_role_signals = sorted({
            signal
            for callee in outbound
            if review_status_by_qn.get(callee, "classification_pending") == "classified"
            for signal in _role_dependency_signals(
                dependency_role_by_qn[qn],
                dependency_role_by_qn.get(callee, "internal_workflow"),
            )
            if signal == "allowed_internal_role_call"
        })
        review_signals = sorted({
            signal
            for callee in outbound
            for signal in _dependency_review_signals(review_status_by_qn.get(callee, "classification_pending"))
        })
        used_by_count = len(inbound)
        calls_count = len(set(outbound))
        layer_consistency = _classify_layer_consistency(
            architecture_layer=function_type,
            callable_kind=callable_kind,
            used_by_count=used_by_count,
            calls_count=calls_count,
            has_architecture_violation=bool(architecture_signals),
        )
        consistency_signal = LAYER_CONSISTENCY_SIGNALS.get(layer_consistency)
        utility_dependency_signal = None
        callable_role_detail = role_tags_by_qn[qn]
        callable_role_group = _callable_role_group(callable_role_detail)
        reachability_kind = (
            "public_entrypoint"
            if qn in public_qn_set
            else "implicit_lifecycle_reachable"
            if review_status == "implicit_lifecycle" or qn in lifecycle_called_qns
            else "unreachable_candidate"
            if review_status == "unreachable"
            else "directly_reachable"
            if used_by_count
            else "unknown_or_entrypoint"
        )
        signals = [
            *architecture_signals,
            *allowed_role_signals,
            *(
                ["implicit_lifecycle_reachability"]
                if "implicit_lifecycle_reachable" in role_tags_by_qn[qn]
                else []
            ),
            *review_signals,
            *refactor.get("signals", []),
            *([consistency_signal] if consistency_signal else []),
            *([utility_dependency_signal] if utility_dependency_signal else []),
        ]
        runtime_reachability = (
            "reachable_from_public_runtime"
            if qn in runtime_reachable_qns or review_status == "implicit_lifecycle" or qn in lifecycle_called_qns
            else "unreachable_runtime_asset"
        )
        if architecture_signals:
            recommended_action = ARCHITECTURE_VIOLATION_ACTION
            priority = "High"
        elif runtime_reachability == "unreachable_runtime_asset":
            recommended_action = "Verify possible orphan"
            priority = "Medium"
        elif review_status == "classification_pending":
            recommended_action = "Next step"
            priority = "Low"
        elif review_status == "implicit_lifecycle":
            recommended_action = "Keep lifecycle method"
            priority = "Low"
        elif review_status == "property_accessor":
            recommended_action = "Keep property accessor"
            priority = "Low"
        elif layer == "public":
            recommended_action = "Public API entrypoint"
            priority = refactor.get("priority", "Low")
        elif layer == "internal":
            recommended_action = "Heavily used helper" if len(inbound) >= 5 else "Shared internal helper" if len(inbound) > 1 else refactor.get("recommended_action", "Next step")
            priority = refactor.get("priority", "Low")
        elif layer == HIDDEN_PRIVATE_LAYER:
            recommended_action, priority = private_helper_action(qn, inbound, outbound)
        elif layer == PUBLIC_CLASS_LAYER:
            recommended_action = "Public config class"
            priority = "Low"
        owner_qn = private_helper_owner(qn, inbound) if layer == HIDDEN_PRIVATE_LAYER else ""
        usage_scope = private_helper_usage_scope(qn, inbound) if layer == HIDDEN_PRIVATE_LAYER else ""
        inventory.append(
            {
                "function_name": node["callable_name"],
                "qualified_name": qn,
                "module": node["module_name"],
                "function_type": function_type,
                "layer": layer,
                "review_status": review_status,
                "review_status_label": (
                    "Cannot trace back to a public callable"
                    if runtime_reachability == "unreachable_runtime_asset"
                    else REVIEW_STATUS_LABELS[review_status]
                ),
                "callable_kind": callable_kind,
                "visibility": "public" if qn in public_qn_set else "private" if node.get("is_underscore") else "internal",
                "callable_role": callable_role_detail,
                "callable_role_group": callable_role_group,
                "callable_role_group_label": ROLE_GROUP_LABELS[callable_role_group],
                "callable_role_detail": callable_role_detail,
                "callable_role_detail_label": ", ".join(_label_from_value(role) for role in callable_role_detail),
                "architectural_role": dependency_role_by_qn[qn],
                "dependency_role": dependency_role_by_qn[qn],
                "owner_qualified_name": owner_qn,
                "owner_function": node_by_qn[owner_qn]["callable_name"] if owner_qn else "",
                "owner_module": node_by_qn[owner_qn]["module_name"] if owner_qn else "",
                "owner_file": _callable_flow_source_path(owner_qn, module_data) if owner_qn else _callable_flow_source_path(qn, module_data),
                "leaks_outside_owner_file": bool(layer == HIDDEN_PRIVATE_LAYER and usage_scope == "cross_module"),
                "usage_scope": usage_scope,
                "usage_scope_label": _label_from_value(usage_scope) if usage_scope else "",
                "reachability": runtime_reachability,
                "reachability_kind": reachability_kind,
                "reachability_label": REACHABILITY_LABELS[reachability_kind],
                "change_risk": priority,
                "refined_recommended_action": recommended_action,
                "recommended_action": recommended_action,
                "priority": priority,
                "signals": signals,
                "architecture_signals": architecture_signals,
                "review_signals": review_signals,
                "used_by_count": used_by_count,
                "called_by_count": used_by_count,
                "call_site_count": refactor.get("call_site_count", sum(1 for caller in inbound for callee in calls_by_qn.get(caller, []) if callee == qn)),
                "recursive": refactor.get("recursive", qn in calls_by_qn.get(qn, [])),
                "repeated_within_single_caller": refactor.get(
                    "repeated_within_single_caller",
                    used_by_count == 1 and bool(inbound) and sum(1 for callee in calls_by_qn.get(next(iter(inbound)), []) if callee == qn) > 1,
                ),
                "calls_count": calls_count,
                "layer_consistency": layer_consistency,
                "layer_consistency_label": LAYER_CONSISTENCY_LABELS[layer_consistency],
                "callers": linked(inbound),
                "callees": linked(set(outbound)),
                "direct_internal_helpers": linked(direct_helper_qns),
                "source_path": _callable_flow_source_path(qn, module_data),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
                **(
                    {
                        "docs_path": f"docs/api/reference/{node['callable_name']}.md",
                        "docs_url": _public_callable_docs_url(node["callable_name"]),
                    }
                    if qn in public_qn_set
                    else {}
                ),
                "deepest_call_chain_depth": public_summary.get("deepest_call_chain_depth") or refactor.get("nesting_level"),
                "repeated_helper_count": public_summary.get("repeated_helper_count", 0),
            }
        )
    deduped_inventory: list[dict[str, Any]] = []
    seen_inventory_identities: set[tuple[str | None, str, int | None, int | None]] = set()
    for row in inventory:
        identity = (
            row.get("source_path"),
            row["qualified_name"],
            row.get("source_start_line"),
            row.get("source_end_line"),
        )
        if identity in seen_inventory_identities:
            continue
        seen_inventory_identities.add(identity)
        deduped_inventory.append(row)
    inventory = deduped_inventory

    summary_counts = {
        "total_callables": len(inventory),
        "total_functions": sum(1 for row in inventory if row["layer"] in CALLABLE_LAYER_LABELS),
        "private_helper_review": sum(1 for row in inventory if row["layer"] == HIDDEN_PRIVATE_LAYER),
        "function_type": {
            label: sum(1 for row in inventory if row["function_type"] == label)
            for label in [*CALLABLE_LAYER_LABELS.values(), PUBLIC_CLASS_LABEL]
        },
        "layer": {
            layer: sum(1 for row in inventory if row["layer"] == layer)
            for layer in CALLABLE_LAYER_LABELS
        },
        "hidden_private_helpers": sum(1 for row in inventory if row["layer"] == HIDDEN_PRIVATE_LAYER),
        "public_classes": sum(1 for row in inventory if row["layer"] == PUBLIC_CLASS_LAYER),
        "review_status": {
            status: sum(1 for row in inventory if row["review_status"] == status)
            for status in REVIEW_STATUS_LABELS
        },
        "callable_kind": {
            label: sum(1 for row in inventory if row["callable_kind"] == label and row["layer"] in CALLABLE_LAYER_LABELS)
            for label in sorted({row["callable_kind"] for row in inventory if row["layer"] in CALLABLE_LAYER_LABELS})
        },
        "callable_role_group": {
            label: sum(1 for row in inventory if row["callable_role_group"] == label)
            for label in sorted({row["callable_role_group"] for row in inventory})
        },
        "callable_role_detail": {
            label: sum(1 for row in inventory if label in row["callable_role_detail"])
            for label in sorted({role for row in inventory for role in row["callable_role_detail"]})
        },
        "callable_role": {
            label: sum(1 for row in inventory if label in row["callable_role"])
            for label in sorted({role for row in inventory for role in row["callable_role"]})
        },
        "dependency_role": {
            label: sum(1 for row in inventory if row["dependency_role"] == label)
            for label in sorted({row["dependency_role"] for row in inventory})
        },
        "recommended_action": {
            label: sum(1 for row in inventory if row["recommended_action"] == label)
            for label in sorted({row["recommended_action"] for row in inventory})
        },
        "layer_consistency": {
            label: sum(1 for row in inventory if row["layer_consistency"] == label)
            for label in LAYER_CONSISTENCY_LABELS
        },
    }
    return summary_counts, inventory


def _build_callable_inventory_metrics(
    summary_counts: dict[str, Any], inventory: list[dict[str, Any]]
) -> dict[str, int]:
    """Return canonical function inventory summary metrics for generated pages."""
    public_api_counts = summary_counts.get("public_api_surface", {})
    total_callables = int(summary_counts.get("total_callables", len(inventory)))
    visible_function_callables = sum(1 for row in inventory if row.get("layer") in CALLABLE_LAYER_LABELS)
    private_helper_review = sum(1 for row in inventory if row.get("layer") == HIDDEN_PRIVATE_LAYER)
    public_class_count = sum(1 for row in inventory if row.get("layer") == PUBLIC_CLASS_LAYER)
    public_api_entrypoints = int(public_api_counts.get("public_api_entrypoints", 0))
    stable_identities = [
        (
            row.get("source_path"),
            row.get("qualified_name"),
            row.get("source_start_line"),
            row.get("source_end_line"),
        )
        for row in inventory
    ]
    unique_inventory_identity_count = len(set(stable_identities))
    return {
        "module_count": len({row.get("source_path") for row in inventory if str(row.get("source_path") or "").endswith(".py")}),
        "total_callables": total_callables,
        "inventory_row_count": len(inventory),
        "unique_inventory_identity_count": unique_inventory_identity_count,
        "duplicate_inventory_identity_count": len(inventory) - unique_inventory_identity_count,
        "public_api_entrypoints": public_api_entrypoints,
        "function_callables": visible_function_callables,
        "supporting_functions": max(visible_function_callables - public_api_entrypoints, 0),
        "public_classes": public_class_count,
        "hidden_private_helpers": private_helper_review,
        "private_helpers_to_review": private_helper_review,
    }


def _callable_inventory_metrics(callable_flow_data: dict[str, Any]) -> dict[str, int]:
    """Read canonical function inventory summary metrics from function graph data."""
    summary_counts = callable_flow_data.get("summary_counts", {})
    metrics = summary_counts.get("callable_inventory_metrics")
    if isinstance(metrics, dict):
        return {
            "module_count": int(metrics.get("module_count", 0)),
            "total_callables": int(metrics.get("total_callables", 0)),
            "public_api_entrypoints": int(metrics.get("public_api_entrypoints", 0)),
            "function_callables": int(metrics.get("function_callables", 0)),
            "supporting_functions": int(metrics.get("supporting_functions", 0)),
            "public_classes": int(metrics.get("public_classes", 0)),
            "hidden_private_helpers": int(metrics.get("hidden_private_helpers", 0)),
        }
    return _build_callable_inventory_metrics(summary_counts, callable_flow_data.get("function_inventory", []))


LONG_CALL_CHAIN_DEPTH_THRESHOLD = 4
LARGE_DEPENDENCY_SURFACE_THRESHOLD = 10

DECISION_RECOMMENDATIONS = {
    "keep_public": "",
    "flatten": "Simplify internals",
    "architecture_violation": "Contains architecture violation",
    "merge": "Inspect helpers marked Maybe combine",
    "move_closer": "Large depth / width",
}

ARCHITECTURE_WARNING_TYPES = (
    "Same-file private dependency",
)

ARCHITECTURE_VIOLATION_TYPES = (
    "Public function calls public function",
    "Shared helper calls public function",
    "Cross-file private dependency",
)

DISPLAY_LABEL_MAP = {
    "Architecture violation": "Broken rule",
    "Architecture violation type": "Broken rule",
    "Long chain": "Too many steps",
    "Many dependencies": "Too many helpers",
    "Shared dependency": "Shared helper",
    "Review for merge": "Maybe combine",
    "Cross-layer dependency": "Broken rule",
    "Cross-layer issue": "Broken rule",
    "Deep chain": "Too many steps",
    "Single-use helper candidate": "Maybe combine",
    "Broken rule": "Broken rule",
    "Broken rule type": "Broken rule",
    "Cross-layer call": "Broken rule",
    "Too many steps": "Too many steps",
    "Too many helpers": "Too many helpers",
    "Maybe combine": "Maybe combine",
    "Used by one function": "Used by one function",
    "Used several times in one function": "Used several times in one function",
    "Recursive helper": "Recursive helper",
    "Heavily used helper": "Heavily used helper",
    "cross_layer_dependency": "Broken rule",
    "deep_chain": "Too many steps",
    "large_downstream_surface": "Too many helpers",
    "single_use_helper_candidate": "Maybe combine",
    "inline_candidate": "Maybe combine",
    "review_abstraction_value": "Used by one function",
}


def _display_label(value: str) -> str:
    """Return the current user-facing label for a legacy finding label."""
    return DISPLAY_LABEL_MAP.get(value, value)


def _decision_layer_group(row: dict[str, Any]) -> str:
    """Return the human-facing layer group from available inventory fields."""
    function_type = row.get("function_type") or row.get("layer")
    if function_type in {"Public function", "Shared helper"}:
        return function_type
    if function_type == PRIVATE_HELPER_LABEL:
        return PRIVATE_HELPER_LABEL
    if function_type == "Supporting object":
        return "Supporting object"
    if function_type == "Public API":
        return "Public function"
    if function_type in {"Shared helper", "Utility"}:
        return "Shared helper"
    layer = row.get("layer")
    if layer in CALLABLE_LAYER_LABELS:
        return CALLABLE_LAYER_LABELS[layer]
    if row.get("callable_kind") != "function" or row.get("layer") == HIDDEN_PRIVATE_LAYER:
        return "Supporting object"
    if row.get("dependency_role") == "public_api":
        return "Public function"
    return "Shared helper"


def _architecture_layer(row: dict[str, Any]) -> str:
    """Return the callable architecture label for a flow row."""
    if row.get("layer") == HIDDEN_PRIVATE_LAYER or row.get("function_type") == PRIVATE_HELPER_LABEL:
        return PRIVATE_HELPER_LABEL
    if row.get("callable_kind") != "function":
        return "Supporting object"
    group = _decision_layer_group(row)
    if group == "Public function":
        return "Public"
    return "Shared helper"


INTERNAL_LAYERING_VIOLATION = "Internal layering violation"
INTERNAL_LAYERING_SUGGESTED_FIX = (
    "Review helpers before changing them. Keep helpers that improve readability, are reused several times inside one "
    "function, call themselves recursively, or are shared across multiple callables."
)

SIMPLE_PUBLIC_CALLABLE = "Public function"
SIMPLE_SHARED_INTERNAL_HELPER = "Shared helper"
SIMPLE_PRIVATE_HELPER = "Private helper"
SIMPLE_REVIEW = "Unknown"


def _simple_flow_classification(row: dict[str, Any], public_user_count: int = 0) -> str:
    """Return the lightweight callable-flow classification shown in generated docs."""
    if _decision_layer_group(row) == "Public function":
        return SIMPLE_PUBLIC_CALLABLE
    if row.get("layer") == HIDDEN_PRIVATE_LAYER or row.get("function_type") == PRIVATE_HELPER_LABEL:
        return SIMPLE_PRIVATE_HELPER
    if _architecture_layer(row) == "Shared helper" and public_user_count > 1:
        return SIMPLE_SHARED_INTERNAL_HELPER
    return SIMPLE_REVIEW


def _classify_architecture_edge(caller_type: str, callee_type: str) -> dict[str, str]:
    """Classify a caller/callee layer pair as allowed unless 2-layer rules override it."""
    if "Supporting object" in {caller_type, callee_type}:
        return {"result": "Allowed", "violation_type": ""}
    return {"result": "Allowed", "violation_type": ""}


def _is_same_owner_private_helper(row: dict[str, Any], public_qn: str) -> bool:
    """Return whether a row is a private helper owned by the selected public callable."""
    return row.get("layer") == HIDDEN_PRIVATE_LAYER and row.get("owner_qualified_name") == public_qn


def _source_file_key(row: dict[str, Any]) -> str:
    """Return the best available file/module identity for callable boundary checks."""
    return str(row.get("source_path") or row.get("owner_file") or row.get("module") or "")


def _same_source_file(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Return whether two callable rows resolve to the same source file/module."""
    left_key = _source_file_key(left)
    right_key = _source_file_key(right)
    return bool(left_key and right_key and left_key == right_key)


def _classify_two_layer_edge(
    *,
    public_qn: str,
    parent_row: dict[str, Any],
    callee_row: dict[str, Any],
    caller_type: str,
    callee_type: str,
    public_user_count: int,
) -> dict[str, str]:
    """Classify whether an edge preserves the two-layer FabricOps callable architecture."""
    base = _classify_architecture_edge(caller_type, callee_type)

    parent_is_public_root = parent_row.get("qualified_name") == public_qn
    parent_is_local_private = _is_same_owner_private_helper(parent_row, public_qn)
    callee_is_local_private = _is_same_owner_private_helper(callee_row, public_qn)
    callee_is_private = callee_row.get("layer") == HIDDEN_PRIVATE_LAYER

    if callee_type == "Public":
        if caller_type == "Public":
            return {"result": "Violation", "violation_type": "Public function calls public function"}
        return {"result": "Violation", "violation_type": "Shared helper calls public function"}

    if callee_is_private:
        if _same_source_file(parent_row, callee_row):
            return {"result": "Warning", "violation_type": "Same-file private dependency"}
        return {"result": "Violation", "violation_type": "Cross-file private dependency"}
    if not (parent_is_public_root or parent_is_local_private) and callee_is_local_private:
        return {"result": "Violation", "violation_type": "Cross-file private dependency"}

    return base


def _architecture_violation_summary(edges: list[dict[str, Any]]) -> dict[str, int]:
    """Return counts by architecture violation direction."""
    keys = list(ARCHITECTURE_VIOLATION_TYPES)
    return {
        key: sum(1 for edge in edges if edge.get("architecture_result") == "Violation" and edge.get("violation_type") == key)
        for key in keys
    }

def _decision_warnings(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> list[str]:
    """Return architecture decision warnings for a public entrypoint flow."""
    warnings: set[str] = set()
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD:
        warnings.add("Too many steps")
    if flow.get("direct_call_count", 0) > LARGE_DEPENDENCY_SURFACE_THRESHOLD:
        warnings.add("Too many helpers")
    if flow["modules_touched_count"] > 4:
        warnings.add("Spans many modules")
    if flow["cross_layer_issue_count"]:
        warnings.add("Broken rule")
    if flow["single_use_helper_candidate_count"]:
        warnings.add("Maybe combine")
    return sorted(warnings)


def _decision_action(flow: dict[str, Any], callee_rows: list[dict[str, Any]]) -> str:
    """Return a public-entrypoint simplification recommendation."""
    if flow["architecture_violation_count"]:
        return DECISION_RECOMMENDATIONS["architecture_violation"]
    if flow["single_use_helper_candidate_count"] and flow["downstream_callable_count"] <= 3:
        return DECISION_RECOMMENDATIONS["merge"]
    if flow["single_use_helper_candidate_count"]:
        return DECISION_RECOMMENDATIONS["move_closer"]
    if flow["maximum_chain_depth"] >= LONG_CALL_CHAIN_DEPTH_THRESHOLD or flow.get("direct_call_count", 0) > LARGE_DEPENDENCY_SURFACE_THRESHOLD or flow["modules_touched_count"] > 4:
        return DECISION_RECOMMENDATIONS["flatten"]
    return DECISION_RECOMMENDATIONS["keep_public"]


def _path_examples(
    root_qn: str,
    target_qn: str,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    limit: int = 3,
) -> list[list[str]]:
    """Return up to ``limit`` readable root-to-target callable path examples."""
    examples: list[list[str]] = []

    def visit(qn: str, path: list[str]) -> None:
        if len(examples) >= limit or len(path) > 12:
            return
        if qn == target_qn:
            examples.append([node_by_qn[item]["callable_name"] for item in path])
            return
        for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
            if child in path:
                continue
            visit(child, [*path, child])

    visit(root_qn, [root_qn])
    return examples[:limit]


def _build_public_entrypoint_flow(
    public_qns: list[str],
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    function_inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build flat public-entrypoint flow records for the decision dashboard."""
    row_by_qn = {row["qualified_name"]: row for row in function_inventory}
    for qn, row in row_by_qn.items():
        row.setdefault("qualified_name", qn)
    flow_visible_qns = {
        qn
        for qn, row in row_by_qn.items()
        if row.get("layer") in CALLABLE_LAYER_LABELS or row.get("layer") == HIDDEN_PRIVATE_LAYER
    }
    visible_helpers_by_public = {
        public_qn: {
            qn
            for qn in _reachable_callables(public_qn, calls_by_qn, node_by_qn)
            if qn in flow_visible_qns and qn in row_by_qn and _decision_layer_group(row_by_qn[qn]) != "Public function"
        }
        for public_qn in public_qns
    }
    public_users_by_helper: dict[str, set[str]] = {}
    for user_public_qn, helper_qns in visible_helpers_by_public.items():
        for helper_qn in helper_qns:
            public_users_by_helper.setdefault(helper_qn, set()).add(user_public_qn)

    callers_by_qn: dict[str, set[str]] = {}
    for caller_qn, callee_qns in calls_by_qn.items():
        for callee_qn in callee_qns:
            if callee_qn in node_by_qn and caller_qn in node_by_qn:
                callers_by_qn.setdefault(callee_qn, set()).add(caller_qn)

    flows: list[dict[str, Any]] = []
    for public_qn in public_qns:
        seen_depth: dict[str, int] = {}
        parent_by_qn: dict[str, str] = {}
        visited_hidden: set[tuple[str, str]] = set()
        queue: list[tuple[str, int, str]] = [
            (callee, 1, public_qn)
            for callee in sorted(set(calls_by_qn.get(public_qn, [])) & set(node_by_qn))
        ]
        while queue:
            qn, depth, parent = queue.pop(0)
            if qn not in row_by_qn or qn not in flow_visible_qns:
                hidden_key = (qn, parent)
                if hidden_key in visited_hidden:
                    continue
                visited_hidden.add(hidden_key)
                for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
                    if child in {public_qn, qn}:
                        continue
                    queue.append((child, depth, parent))
                continue
            if qn in seen_depth and seen_depth[qn] <= depth:
                continue
            seen_depth[qn] = depth
            parent_by_qn[qn] = parent
            for child in sorted(set(calls_by_qn.get(qn, [])) & set(node_by_qn)):
                if child in {public_qn, qn}:
                    continue
                queue.append((child, depth + 1, qn))

        flow_qns = {public_qn, *seen_depth}
        inside_callers_by_qn = {
            qn: sorted(callers_by_qn.get(qn, set()) & flow_qns)
            for qn in seen_depth
        }
        inside_callees_by_qn = {
            qn: sorted(set(calls_by_qn.get(qn, [])) & flow_qns)
            for qn in seen_depth
        }
        outside_callers_by_qn = {
            qn: sorted(callers_by_qn.get(qn, set()) - flow_qns)
            for qn in seen_depth
        }

        def callee_row(qn: str, edge_type: str) -> dict[str, Any]:
            row = row_by_qn[qn]
            parent_row = row_by_qn.get(parent_by_qn.get(qn, public_qn), row_by_qn[public_qn])
            signals = list(row.get("signals", []))
            if _architecture_layer(row_by_qn.get(parent_by_qn.get(qn, ""), {})) == "Internal" and _architecture_layer(row) == "Internal":
                signals = sorted({*signals, "internal_helper_chain"})
            caller_type = _architecture_layer(parent_row)
            callee_type = _architecture_layer(row)
            edge_classification = _classify_two_layer_edge(
                public_qn=public_qn,
                parent_row=parent_row,
                callee_row=row,
                caller_type=caller_type,
                callee_type=callee_type,
                public_user_count=len(public_users_by_helper.get(qn, set())),
            )
            return {
                "callable": row["function_name"],
                "function_name": row["function_name"],
                "qualified_name": qn,
                "module": row["module"],
                "depth": seen_depth[qn],
                "layer": row.get("layer"),
                "function_type": row.get("function_type"),
                "layer_group": _decision_layer_group(row),
                "simple_classification": _simple_flow_classification(row, len(public_users_by_helper.get(qn, set()))),
                "edge_type": edge_type,
                "parent_qualified_name": parent_by_qn.get(qn, public_qn),
                "caller_type": caller_type,
                "callee_type": callee_type,
                "architecture_result": edge_classification["result"],
                "violation_type": edge_classification["violation_type"],
                "signals": signals,
                "architecture_signals": row.get("architecture_signals", []),
                "recommended_action": row.get("recommended_action"),
                "called_inside_flow_by": len(inside_callers_by_qn.get(qn, [])),
                "calls_inside_flow": len(inside_callees_by_qn.get(qn, [])),
                "used_outside_flow": len(outside_callers_by_qn.get(qn, [])),
                "is_end_node": len(inside_callees_by_qn.get(qn, [])) == 0,
                "downstream_count": row.get("calls_count", 0),
                "source_path": _callable_flow_source_path(qn, module_data),
                "source_url": _callable_flow_source_link(qn, module_data),
                **_callable_flow_source_location(qn, module_data),
                **({"docs_path": row["docs_path"], "docs_url": row["docs_url"]} if row.get("docs_url") else {}),
                "path_examples": _path_examples(public_qn, qn, calls_by_qn, node_by_qn),
                "call_site_count": row.get("call_site_count", 0),
                "recursive": bool(row.get("recursive", False)),
                "repeated_within_single_caller": bool(row.get("repeated_within_single_caller", False)),
                "helper_cleanup_candidate": _decision_layer_group(row) != "Public function"
                and row_by_qn[qn].get("used_by_count", 0) == 1
                and row.get("call_site_count", 0) == 1
                and not row.get("recursive", False),
            }

        direct_qns = sorted(
            (qn for qn, depth in seen_depth.items() if depth == 1),
            key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
        )
        transitive_qns = sorted(
            seen_depth,
            key=lambda qn: (seen_depth[qn], node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower(), qn),
        )
        callee_rows = [callee_row(qn, "transitive" if seen_depth[qn] > 1 else "direct") for qn in transitive_qns]
        source_python_files = sorted(
            {
                path
                for qn in {public_qn, *seen_depth}
                if (path := _callable_flow_source_path(qn, module_data)) and path.endswith(".py")
            }
        )
        modules_touched = sorted({node_by_qn[public_qn]["module_name"], *(node_by_qn[qn]["module_name"] for qn in seen_depth)})
        flow = {
            "public_callable": node_by_qn[public_qn]["callable_name"],
            "function_name": node_by_qn[public_qn]["callable_name"],
            "qualified_name": public_qn,
            "module": node_by_qn[public_qn]["module_name"],
            "docs_path": f"docs/api/reference/{node_by_qn[public_qn]['callable_name']}.md",
            "docs_url": _public_callable_docs_url(node_by_qn[public_qn]["callable_name"]),
            "source_path": _callable_flow_source_path(public_qn, module_data),
            "owner_file": _callable_flow_source_path(public_qn, module_data),
            "source_url": _callable_flow_source_link(public_qn, module_data),
            **_callable_flow_source_location(public_qn, module_data),
            "direct_call_count": len(direct_qns),
            "width": len(direct_qns),
            "scope_asset_count": len(flow_qns),
            "scope": len(flow_qns),
            "downstream_callable_count": len(seen_depth),
            "maximum_chain_depth": max(seen_depth.values(), default=0),
            "modules_touched_count": len(source_python_files),
            "modules_touched": modules_touched,
            "source_python_files": source_python_files,
            "external_dependents_count": sum(1 for qn in seen_depth if outside_callers_by_qn.get(qn)),
            "end_node_count": sum(1 for qn in seen_depth if not inside_callees_by_qn.get(qn)),
            "architecture_violation_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "architecture_violation_breakdown": _architecture_violation_summary(callee_rows),
            "cross_layer_issue_count": sum(1 for row in callee_rows if row.get("architecture_result") == "Violation"),
            "single_use_helper_candidate_count": sum(
                1
                for row in callee_rows
                if row["layer_group"] != "Public function"
                and row_by_qn[row["qualified_name"]].get("used_by_count", 0) == 1
                and row.get("call_site_count", 0) == 1
                and not row.get("recursive", False)
            ),
            "recommended_simplification_action": "",
            "warnings": [],
            "direct_callees": [callee_row(qn, "direct") for qn in direct_qns],
            "transitive_callees": callee_rows,
            "private_helper_review_items": [
                row
                for row in function_inventory
                if row.get("layer") == HIDDEN_PRIVATE_LAYER and row.get("owner_qualified_name") == public_qn
            ],
        }
        flow["selection_keys"] = _public_flow_selection_keys(flow)
        flow["recommended_simplification_action"] = _decision_action(flow, callee_rows)
        flow["warnings"] = _decision_warnings(flow, callee_rows)
        flows.append(flow)
    return flows


CALLABLE_FLOW_TOP_LEVEL_KEYS = (
    "metadata",
    "architecture_thresholds",
    "function_inventory",
    "public_entrypoint_flow",
    "summary_counts",
    "inventory_row_count",
    "unique_inventory_identity_count",
    "duplicate_inventory_identity_count",
)

CALLABLE_FLOW_SUMMARY_KEYS = (
    "total_callables",
    "function_type",
    "layer",
    "review_status",
    "callable_kind",
    "callable_role_group",
    "dependency_role",
    "recommended_action",
    "public_api_surface",
    "callable_inventory_metrics",
    "private_helper_review",
    "public_classes",
)

FUNCTION_INVENTORY_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "source_path",
    "owner_file",
    "source_url",
    "source_start_line",
    "source_end_line",
    "function_type",
    "layer",
    "review_status",
    "review_status_label",
    "callable_kind",
    "callable_role",
    "callable_role_group",
    "callable_role_group_label",
    "callable_role_detail",
    "callable_role_detail_label",
    "dependency_role",
    "owner_qualified_name",
    "owner_function",
    "owner_module",
    "leaks_outside_owner_file",
    "usage_scope",
    "usage_scope_label",
    "reachability",
    "reachability_kind",
    "reachability_label",
    "recommended_action",
    "priority",
    "signals",
    "architecture_signals",
    "review_signals",
    "called_by_count",
    "call_site_count",
    "recursive",
    "repeated_within_single_caller",
    "calls_count",
    "callers",
    "callees",
    "docs_path",
    "docs_url",
)

PUBLIC_ENTRYPOINT_FLOW_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "docs_path",
    "docs_url",
    "source_path",
    "owner_file",
    "source_url",
    "source_start_line",
    "source_end_line",
    "priority",
    "recommended_simplification_action",
    "warnings",
    "width",
    "direct_call_count",
    "scope",
    "scope_asset_count",
    "downstream_count",
    "max_depth",
    "modules_touched",
    "source_python_files",
    "selection_keys",
    "external_dependents_count",
    "end_node_count",
    "architecture_violation_count",
    "architecture_violation_breakdown",
    "helper_cleanup_candidates",
    "direct_callees",
    "transitive_callees",
    "private_helper_review_items",
)

PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS = (
    "qualified_name",
    "function_name",
    "module",
    "depth",
    "function_type",
    "layer",
    "layer_group",
    "simple_classification",
    "edge_type",
    "parent_qualified_name",
    "caller_type",
    "callee_type",
    "architecture_result",
    "violation_type",
    "signals",
    "recommended_action",
    "called_inside_flow_by",
    "call_site_count",
    "recursive",
    "repeated_within_single_caller",
    "calls_inside_flow",
    "used_outside_flow",
    "is_end_node",
    "downstream_count",
    "source_path",
    "source_url",
    "source_start_line",
    "source_end_line",
    "docs_path",
    "docs_url",
    "path_examples",
    "helper_cleanup_candidate",
)


def _callable_flow_source_context() -> dict[str, str]:
    """Return safe Git source context for generated callable-flow assets."""
    context: dict[str, str] = {}
    commands = (
        ("commit", ["git", "rev-parse", "--short", "HEAD"]),
        ("branch", ["git", "branch", "--show-current"]),
    )
    for key, command in commands:
        try:
            value = subprocess.check_output(
                command,
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            continue
        if value:
            context[key] = value
    return context


def _callable_flow_metadata(generated_at_utc: datetime) -> dict[str, Any]:
    """Return generation metadata shared by callable-flow JSON and HTML assets."""
    metadata: dict[str, Any] = {
        "generated_at_utc": generated_at_utc.isoformat().replace("+00:00", "Z"),
        "data_source": "public-function-call-flows.json",
    }
    return metadata


def _dashboard_contract_row(row: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    """Return ``row`` trimmed to the public dashboard data contract."""
    return {key: row[key] for key in keys if key in row}


def _metadata_table_title(table_name: str) -> str:
    """Return a human-readable metadata table title."""
    return table_name.replace("_", " ").title()


def _metadata_owner_specs(
    table_name: str,
    column_name: str,
    column_owners: dict[str, dict[str, list[Any]]],
) -> list[Any]:
    """Return structured owner specs for one metadata column."""
    owner_map = column_owners.get(table_name)
    if owner_map is None:
        raise RuntimeError(f"Missing METADATA_COLUMN_OWNERS entry for {table_name}")
    if column_name in AUDIT_FIELD_DESCRIPTIONS and "__audit__" in owner_map:
        return owner_map["__audit__"]
    if column_name in owner_map:
        return owner_map[column_name]
    if "__default__" in owner_map:
        return owner_map["__default__"]
    raise RuntimeError(f"Missing metadata owner mapping for {table_name}.{column_name}")


def _render_metadata_owner(
    owner: Any,
    *,
    public_callable_set: set[str],
) -> str:
    """Render one metadata owner as public link, code reference, or fallback label."""
    if isinstance(owner, str):
        if owner.startswith(f"{PACKAGE_NAME}."):
            module_name, callable_name = owner.rsplit(".", 1)
            source_path = ROOT / "src" / Path(*module_name.split(".")).with_suffix(".py")
            if not source_path.exists():
                raise RuntimeError(f"Metadata owner source module does not exist: {owner}")
            module_tree = ast.parse(source_path.read_text(encoding="utf-8"))
            if not any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == callable_name
                for node in module_tree.body
            ):
                raise RuntimeError(f"Metadata owner callable does not exist in source: {owner}")
        simple_name = owner.rsplit(".", 1)[-1]
        if simple_name in public_callable_set:
            return f"[`{simple_name}`](../../api/reference/{simple_name}.md)"
        return f"`{owner}`"
    if isinstance(owner, dict):
        label = str(owner.get("label", "")).strip()
        reason = str(owner.get("reason", "")).strip()
        if not label or not reason:
            raise RuntimeError("Metadata owner label entries must define non-empty label and reason values.")
        return label
    raise RuntimeError(f"Unsupported metadata owner entry: {owner!r}")


def _metadata_managed_by(
    table_name: str,
    column_name: str,
    *,
    column_owners: dict[str, dict[str, list[Any]]],
    public_callable_set: set[str],
) -> str:
    """Return rendered metadata owner text for a generated metadata column row."""
    rendered = []
    seen = set()
    for owner in _metadata_owner_specs(table_name, column_name, column_owners):
        text = _render_metadata_owner(owner, public_callable_set=public_callable_set)
        if text not in seen:
            seen.add(text)
            rendered.append(text)
    return ", ".join(rendered)


def _metadata_field_description(table_name: str, column_name: str) -> str:
    """Return generated metadata column guidance."""
    if column_name in AUDIT_FIELD_DESCRIPTIONS:
        return AUDIT_FIELD_DESCRIPTIONS[column_name]
    if column_name in METADATA_FIELD_DESCRIPTIONS:
        return METADATA_FIELD_DESCRIPTIONS[column_name]
    if column_name.endswith("_json"):
        return f"JSON payload stored for `{column_name}`."
    if column_name.endswith("_id"):
        return f"Identifier stored for `{column_name}`."
    if column_name.endswith("_name"):
        return f"Human-readable name stored for `{column_name}`."
    if column_name.endswith("_at"):
        return f"Timestamp stored for `{column_name}`."
    if column_name.endswith("_date"):
        return f"Date stored for `{column_name}`."
    if column_name.startswith("is_") or column_name.startswith("requires_"):
        return f"Boolean state recorded for `{column_name}`."
    return f"{_metadata_table_title(table_name)} field `{column_name}`."


def _metadata_table_purpose(table_name: str, table_purposes: dict[str, str]) -> str:
    """Return generated metadata table purpose text."""
    return table_purposes.get(table_name, f"{_metadata_table_title(table_name)} metadata table.")


def generate_metadata_reference_pages() -> None:
    """Generate metadata table reference pages from the canonical schema registry."""
    from fabricops_kit.config.metadata_schemas import (
        CANONICAL_METADATA_TABLES,
        metadata_table_schema_registry,
        metadata_table_schema_rows,
    )

    METADATA_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    registry = metadata_table_schema_registry()
    canonical_tables = list(CANONICAL_METADATA_TABLES)
    missing_tables = [table_name for table_name in canonical_tables if table_name not in registry]
    if missing_tables:
        raise RuntimeError(
            "metadata_table_schema_registry() is missing canonical metadata tables: "
            + ", ".join(missing_tables)
        )
    table_purposes, column_owners = parse_metadata_reference_contract()
    public_callable_set = public_callable_names()
    for generated_page in METADATA_REFERENCE_DIR.glob("*.md"):
        generated_page.unlink(missing_ok=True)
    index_lines = [
        "# List of Metadata Tables",
        "",
        *parse_metadata_reference_overview(),
        "",
        "<div class=\"grid cards\" markdown>",
        "",
    ]
    for table_name in canonical_tables:
        slug = table_name.lower()
        purpose = _metadata_table_purpose(table_name, table_purposes)
        index_lines.extend([
            f"-   **[{table_name}](metadata/{slug}.md)**",
            "",
            f"    {purpose}",
            "",
        ])
        rows = metadata_table_schema_rows(registry[table_name])
        lines = [
            f"# {table_name}",
            "",
            f"**Purpose:** {purpose}",
            "",
            "## Implemented schema",
            "",
            "| Column | Data type | Managed by | Description |",
            "| --- | --- | --- | --- |",
        ]
        for row in rows:
            column = str(row["name"])
            lines.append(
                f"| `{column}` | `{row['type']}` | "
                f"{_metadata_managed_by(table_name, column, column_owners=column_owners, public_callable_set=public_callable_set)} | "
                f"{_metadata_field_description(table_name, column)} |"
            )
        related_functions = METADATA_RELATED_FUNCTIONS.get(table_name, [])
        if related_functions:
            lines.extend(["", "## Related function reference", ""])
            lines.extend(
                f"- [`{function_name}`](../../api/reference/{function_name}.md)"
                for function_name in related_functions
            )
        (METADATA_REFERENCE_DIR / f"{slug}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    index_lines.extend(["</div>", ""])
    METADATA_REFERENCE_INDEX_PATH.write_text("\n".join(index_lines), encoding="utf-8")


def _trim_callable_flow_dashboard_contract(
    callable_flow_data: dict[str, Any],
    node_by_qn: dict[str, dict[str, Any]] | None = None,
    module_data: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return compact callable-flow JSON consumed by generated dashboards."""
    summary_counts = callable_flow_data["summary_counts"]
    public_surface = dict(summary_counts.get("public_api_surface", {}))
    public_surface.pop("deep_chains", None)
    public_surface.pop("cross_layer_issues", None)
    public_surface.pop("single_use_helper_candidates", None)
    trimmed_summary = {
        key: summary_counts[key]
        for key in CALLABLE_FLOW_SUMMARY_KEYS
        if key in summary_counts
    }
    trimmed_summary["public_api_surface"] = public_surface

    inventory = [
        _dashboard_contract_row(row, FUNCTION_INVENTORY_DASHBOARD_KEYS)
        for row in callable_flow_data["function_inventory"]
    ]

    public_flows = []
    for flow in callable_flow_data["public_entrypoint_flow"]:
        trimmed_flow = dict(flow)
        trimmed_flow["function_name"] = flow.get("function_name", flow.get("public_callable"))
        trimmed_flow["selection_keys"] = _public_flow_selection_keys(trimmed_flow)
        trimmed_flow["width"] = flow.get("width", flow.get("direct_call_count", 0))
        trimmed_flow["direct_call_count"] = flow.get("direct_call_count", trimmed_flow["width"])
        trimmed_flow["scope"] = flow.get("scope", flow.get("scope_asset_count", 0))
        trimmed_flow["scope_asset_count"] = flow.get("scope_asset_count", trimmed_flow["scope"])
        trimmed_flow["downstream_count"] = flow.get("downstream_count", flow.get("downstream_callable_count", 0))
        trimmed_flow["max_depth"] = flow.get("max_depth", flow.get("maximum_chain_depth", 0))
        trimmed_flow["priority"] = "High" if flow.get("architecture_violation_count") else "Medium" if flow.get("warnings") else "Low"
        trimmed_flow["helper_cleanup_candidates"] = flow.get("helper_cleanup_candidates", flow.get("single_use_helper_candidate_count", 0))
        trimmed_flow["private_helper_review_items"] = [
            _dashboard_contract_row(item, FUNCTION_INVENTORY_DASHBOARD_KEYS)
            for item in flow.get("private_helper_review_items", [])
        ]
        trimmed_flow["direct_callees"] = [
            _dashboard_contract_row({**callee, "function_name": callee.get("function_name", callee.get("callable"))}, PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS)
            for callee in flow.get("direct_callees", [])
        ]
        trimmed_flow["transitive_callees"] = [
            _dashboard_contract_row({**callee, "function_name": callee.get("function_name", callee.get("callable"))}, PUBLIC_FLOW_CALLEE_DASHBOARD_KEYS)
            for callee in flow.get("transitive_callees", [])
        ]
        public_flows.append(_dashboard_contract_row(trimmed_flow, PUBLIC_ENTRYPOINT_FLOW_DASHBOARD_KEYS))

    metrics = trimmed_summary.get("callable_inventory_metrics", {})
    # Keep the embedded dashboard contract lean. The dashboard JS still accepts
    # legacy `public_flows` as a read-only fallback, but new generated assets
    # should not duplicate the public-entrypoint payload under two top-level keys.
    compact = {
        "metadata": callable_flow_data["metadata"],
        "architecture_thresholds": callable_flow_data["architecture_thresholds"],
        "function_inventory": inventory,
        "public_entrypoint_flow": public_flows,
        "summary_counts": trimmed_summary,
        "inventory_row_count": metrics.get("inventory_row_count", len(inventory)),
        "unique_inventory_identity_count": metrics.get("unique_inventory_identity_count", len(inventory)),
        "duplicate_inventory_identity_count": metrics.get("duplicate_inventory_identity_count", 0),
    }
    return {key: compact[key] for key in CALLABLE_FLOW_TOP_LEVEL_KEYS}

def _build_callable_flow_data(
    public_qns: list[str],
    public_class_qns: list[str] | None,
    calls_by_qn: dict[str, list[str]],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
    *,
    generated_at_utc: datetime,
) -> dict[str, Any]:
    """Build the global public function call graph map from existing call graph data."""
    public_qn_set = set(public_qns)
    reachable_by_public: dict[str, set[str]] = {}
    helpers_by_public: dict[str, set[str]] = {}
    public_dependencies: dict[str, list[dict[str, str]]] = {}
    helper_users: dict[str, set[str]] = {}
    summary: list[dict[str, Any]] = []

    for public_qn in public_qns:
        public_name = node_by_qn[public_qn]["callable_name"]
        reachable = _reachable_callables(public_qn, calls_by_qn, node_by_qn)
        reachable_by_public[public_qn] = reachable
        helper_qns = set(_callable_flow_internal_helper_qns(public_qn, calls_by_qn, node_by_qn))
        helpers_by_public[public_qn] = helper_qns
        for helper_qn in helper_qns:
            helper_users.setdefault(helper_qn, set()).add(public_qn)
        public_deps = sorted(
            (qn for qn in reachable if qn in public_qn_set and qn != public_qn),
            key=lambda qn: node_by_qn[qn]["callable_name"].lower(),
        )
        public_dependencies[public_name] = [
            {
                "callable": node_by_qn[dep_qn]["callable_name"],
                "qualified_name": dep_qn,
                "module": node_by_qn[dep_qn]["module_name"],
                "docs_path": f"docs/api/reference/{node_by_qn[dep_qn]['callable_name']}.md",
                "docs_url": _public_callable_docs_url(node_by_qn[dep_qn]['callable_name']),
            }
            for dep_qn in public_deps
        ]

    shared_helper_qns = {helper_qn for helper_qn, users in helper_users.items() if len(users) > 1}
    for public_qn in public_qns:
        public_name = node_by_qn[public_qn]["callable_name"]
        direct_helpers = sorted(
            {
                qn
                for qn in calls_by_qn.get(public_qn, [])
                if qn in node_by_qn
                and qn not in INTERNAL_HELPER_EXCLUSIONS.get(public_name, set())
                and _is_internal_helper_qn(qn, node_by_qn)
            },
            key=lambda qn: (node_by_qn[qn]["module_name"], node_by_qn[qn]["callable_name"].lower()),
        )
        refactor_signals = _collect_refactor_signals(
            public_qn,
            calls_by_qn,
            node_by_qn,
            module_data,
            excluded_helpers=INTERNAL_HELPER_EXCLUSIONS.get(public_name, set()),
        )
        summary.append(
            {
                "callable": public_name,
                "qualified_name": public_qn,
                "module": node_by_qn[public_qn]["module_name"],
                "docs_path": f"docs/api/reference/{public_name}.md",
                "docs_url": _public_callable_docs_url(public_name),
                "unique_internal_helper_count": len(helpers_by_public[public_qn]),
                "unique_internal_helpers": [
                    {
                        "helper": node_by_qn[helper_qn]["callable_name"],
                        "qualified_name": helper_qn,
                        "module": node_by_qn[helper_qn]["module_name"],
                        "source_url": _callable_flow_source_link(helper_qn, module_data),
                    }
                    for helper_qn in _callable_flow_internal_helper_qns(public_qn, calls_by_qn, node_by_qn)
                ],
                "direct_internal_helpers": [
                    {
                        "helper": node_by_qn[helper_qn]["callable_name"],
                        "qualified_name": helper_qn,
                        "module": node_by_qn[helper_qn]["module_name"],
                        "source_url": _callable_flow_source_link(helper_qn, module_data),
                    }
                    for helper_qn in direct_helpers
                ],
                "deepest_call_chain_depth": _deepest_call_chain_depth(public_qn, calls_by_qn, node_by_qn),
                "repeated_helper_count": len(refactor_signals["repeated_helpers"]),
                "calls_public_callable": bool(public_dependencies[public_name]),
                "public_callables_called": public_dependencies[public_name],
                "shared_helper_overlap_count": len(helpers_by_public[public_qn] & shared_helper_qns),
            }
        )

    _, refactor_inventory, _ = _build_refactor_inventory(
        public_qns,
        public_class_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
    )

    summary_counts, function_inventory = _build_function_inventory(
        public_qns,
        public_class_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        summary,
        refactor_inventory,
    )
    public_entrypoint_flow = _build_public_entrypoint_flow(
        public_qns,
        calls_by_qn,
        node_by_qn,
        module_data,
        function_inventory,
    )
    summary_counts["public_api_surface"] = {
        "public_api_entrypoints": len(public_entrypoint_flow),
        "long_call_chains": sum(1 for flow in public_entrypoint_flow if "Too many steps" in flow["warnings"]),
        "architecture_violations": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "architecture_findings": sum(1 for flow in public_entrypoint_flow if flow["architecture_violation_count"]),
        "review_for_merge_helpers": sum(1 for flow in public_entrypoint_flow if flow["single_use_helper_candidate_count"]),
        "suggested_helper_review": sum(
            1
            for flow in public_entrypoint_flow
            if flow["recommended_simplification_action"]
            in {DECISION_RECOMMENDATIONS["merge"], DECISION_RECOMMENDATIONS["move_closer"]}
        ),
    }
    summary_counts["callable_inventory_metrics"] = _build_callable_inventory_metrics(summary_counts, function_inventory)

    full_contract = {
        "metadata": _callable_flow_metadata(generated_at_utc),
        "function_inventory": function_inventory,
        "public_entrypoint_flow": public_entrypoint_flow,
        "summary_counts": summary_counts,
        "architecture_thresholds": {
            "long_call_chain_depth": LONG_CALL_CHAIN_DEPTH_THRESHOLD,
            "large_dependency_surface": LARGE_DEPENDENCY_SURFACE_THRESHOLD,
        },
    }
    return _trim_callable_flow_dashboard_contract(full_contract, node_by_qn, module_data)


def _public_callable_docs_url(callable_name: str) -> str:
    """Return the callable-flow relative URL for a public API reference page."""
    return f"../../api/reference/{callable_name}/"


def _render_link(label: str, url: str | None = None, *, code: bool = True) -> str:
    """Render an HTML link or code span for generated callable-flow tables."""
    text = html.escape(label)
    inner = f"<code>{text}</code>" if code else text
    if not url:
        return inner
    return f'<a href="{html.escape(url, quote=True)}">{inner}</a>'


def _indent_markdown(lines: list[str], spaces: int = 4) -> list[str]:
    """Indent every physical Markdown line for MkDocs Material blocks."""
    prefix = " " * spaces
    indented: list[str] = []
    for item in lines:
        physical_lines = item.split("\n")
        indented.extend("" if line == "" else f"{prefix}{line}" for line in physical_lines)
    return indented


def _helper_area(helper_name: str, purpose: str) -> tuple[str, str]:
    """Return the implementation area and plain-English role for an internal helper."""
    haystack = f"{helper_name} {purpose}".lower()
    if helper_name in {"_guardrail_exclude_columns", "resolve_profiled_columns"} or "exclude_columns" in haystack:
        return "Column handling", "Select, exclude, and normalize column names used by the callable."
    if helper_name in {
        "_catalogue_value",
        "_comparable_value",
        "_is_greater_than",
        "_is_less_than",
        "_latest_catalogue_behavior_profile_row",
        "_profile_row_count",
        "_profile_watermark_bounds",
        "_row_to_dict",
        "_string_value",
    }:
        return "Profile comparison", "Compare current evidence with accepted profile values and behavior baselines."
    if any(token in haystack for token in ("audit", "timestamp", "timezone")):
        return "Audit timestamp", "Resolve and stamp audit time consistently."
    if any(
        token in haystack
        for token in ("metadata", "load", "table", "database", "registered", "warehouse", "lakehouse")
    ):
        return "Metadata loading", "Load and identify the metadata or table context needed by the callable."
    if any(token in haystack for token in ("valid", "required", "check", "ensure")):
        return "Validation", "Validate inputs and guard conditions before the workflow continues."
    if any(token in haystack for token in ("parse", "normalise", "normalize", "canonical", "json", "name")):
        return "Rule parsing", "Normalize stored or user-provided values before applying rules."
    if any(token in haystack for token in ("rule", "condition", "evaluate", "sql", "dq", "expectation")):
        return "Rule evaluation", "Convert configured rules into executable checks and evaluation results."
    if any(token in haystack for token in ("summary", "summar", "status", "failed", "message", "result")):
        return "Result summary", "Build final statuses, counts, and messages for the caller."
    if any(token in haystack for token in ("spark", "fabric", "session")):
        return "Fabric or Spark access", "Access Fabric or Spark runtime services used by the implementation."
    return "Other", "Support lower-level implementation details that do not fit the main helper areas."


def _ordered_helper_areas(area_names: Iterable[str]) -> list[str]:
    """Sort helper areas in the documented reference order."""
    preferred = [
        "Audit timestamp",
        "Metadata loading",
        "Validation",
        "Rule parsing",
        "Profile comparison",
        "Column handling",
        "Rule evaluation",
        "Result summary",
        "Fabric or Spark access",
        "Other",
    ]
    rank = {name: index for index, name in enumerate(preferred)}
    return sorted(area_names, key=lambda name: (rank.get(name, len(preferred)), name.lower()))


def _helper_area_purposes(area_names: list[str]) -> str:
    """Return a compact human-readable list of grouped helper purposes."""
    labels = [name.lower() for name in area_names]
    if not labels:
        return "implementation support"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{', '.join(labels[:-1])}, and {labels[-1]}"


def _helper_chip(helper: dict[str, Any]) -> str:
    """Return a wrapped, clickable helper chip for grouped implementation summaries."""
    source_location = helper["source_location"]
    source_url = github_source_url(
        helper["source_path"],
        source_location.get("start_line"),
        source_location.get("end_line"),
    )
    return (
        f'<a class="reference-helper-chip" href="{html_escape(source_url)}">'
        f'<code>{html_escape(helper["name"])}</code>'
        "</a>"
    )


def _render_helper_group_cards(grouped: dict[str, dict[str, Any]], area_order: list[str]) -> list[str]:
    """Render internal helpers as responsive grouped cards instead of a wide table."""
    lines = ['<div class="reference-helper-groups">']
    for area in area_order:
        helpers = grouped[area]["helpers"]
        lines.extend(
            [
                '  <section class="reference-helper-group">',
                f'    <h4>{html_escape(area)}</h4>',
                f'    <p>{html_escape(grouped[area]["role"])}</p>',
                '    <div class="reference-helper-chip-wrap">',
            ]
        )
        for helper in helpers:
            lines.append(f"      {_helper_chip(helper)}")
        lines.extend(["    </div>", "  </section>"])
    lines.append("</div>")
    return lines


def _helper_group_summary_lines(
    root_qn: str,
    helper_qns: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render grouped helper cards for internal helpers used by a callable."""
    root_name = node_by_qn[root_qn]["callable_name"]
    helper_count = len(helper_qns)
    if not helper_qns:
        return [
            (
                f"This callable uses 0 internal helpers; `{root_name}` does not have package-local "
                "helper descendants in the generated call graph."
            ),
            "",
            '<div class="reference-helper-groups">',
            '  <section class="reference-helper-group reference-helper-group-empty">',
            '    <h4>No internal helpers detected</h4>',
            '    <p>This callable does not have package-local helper descendants in the generated call graph.</p>',
            "  </section>",
            "</div>",
        ]

    grouped: dict[str, dict[str, Any]] = {}
    for helper_qn in helper_qns:
        helper_node = node_by_qn[helper_qn]
        helper_name = helper_node["callable_name"]
        module_name = helper_node["module_name"]
        info = module_data[module_name]
        purpose = info.get("functions", {}).get(helper_name) or "Implementation helper used by the package implementation."
        area, role = _helper_area(helper_name, purpose)
        grouped.setdefault(area, {"role": role, "helpers": []})["helpers"].append(
            {
                "name": helper_name,
                "module_name": module_name,
                "source_path": info.get("source_path") or f"src/fabricops_kit/{module_name.replace('.', '/')}.py",
                "source_location": info.get("source_locations", {}).get(helper_name, {}),
            }
        )

    area_order = _ordered_helper_areas(grouped)
    for area in area_order:
        grouped[area]["helpers"] = sorted(grouped[area]["helpers"], key=lambda item: item["name"].lower())

    return [
        f"This callable uses {helper_count} internal helpers for {_helper_area_purposes(area_order)}.",
        "",
        *_render_helper_group_cards(grouped, area_order),
    ]


def _render_nested_helper_section(
    root_qn: str,
    helper_qns: list[str],
    node_by_qn: dict[str, dict[str, Any]],
    module_data: dict[str, dict[str, Any]],
) -> list[str]:
    """Render a collapsed grouped summary for internal helpers used by a callable."""
    return [
        f'??? info "Implementation helpers used: {len(helper_qns)}"',
        "",
        *_indent_markdown(_helper_group_summary_lines(root_qn, helper_qns, node_by_qn, module_data)),
    ]


def function_chip_wrap(chips: list[str]) -> str:
    """Return a mobile-friendly chip wrapper for a generated docs table cell."""
    if not chips:
        return "—"
    return '<span class="function-chip-wrap">' + "".join(chips) + "</span>"


def parse_simple_yaml(path: Path) -> dict[str, dict[str, Any]]:
    """Parse a small YAML subset used for function usage overrides."""
    data: dict[str, dict[str, Any]] = {}
    current_key: str | None = None
    current_list_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            if not line.endswith(":"):
                continue
            current_key = line[:-1].strip()
            data[current_key] = {}
            current_list_key = None
            continue
        if current_key is None:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current_list_key:
                data[current_key].setdefault(current_list_key, []).append(stripped[2:].strip())
            continue
        if ":" in stripped:
            key, value = [p.strip() for p in stripped.split(":", 1)]
            if value == "":
                data[current_key][key] = []
                current_list_key = key
            else:
                data[current_key][key] = value
                current_list_key = None
    return data

def render_callable_map_page(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], module_summary: list[dict[str, Any]]) -> str:
    """Render callable map page."""
    module_edges = sorted(
        {
            (e["caller_qualified_name"].split(".")[-2], e["callee_qualified_name"].split(".")[-2])
            for e in edges
            if e["callee_qualified_name"] and e["edge_type"] == "cross_module"
        }
    )
    public_nodes = sorted([n for n in nodes if n["exported"]], key=lambda x: (x["module_name"], x["callable_name"]))
    helper_nodes = sorted([n for n in nodes if n["callable_name"].startswith("_")], key=lambda x: (x["module_name"], x["callable_name"]))
    cross_edges = sorted(
        [e for e in edges if e["callee_qualified_name"] and e["edge_type"] == "cross_module"],
        key=lambda x: (x["caller_qualified_name"], x["callee_qualified_name"]),
    )

    lines = [
        "# Callable Map (Developer Diagnostic)",
        "",
        "This page is generated from FabricOps source code using static AST parsing.",
        "",
        "> Developer diagnostic only. Primary user documentation now lives on Function Reference and module pages.",
        "",
        "## 1. Module dependency graph (diagnostic)",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for caller, callee in module_edges:
        lines.append(f"  {caller} --> {callee}")

    lines.extend(["```", "", "## 2. Public callables grouped by module", ""])
    by_mod: dict[str, list[str]] = {}
    for node in public_nodes:
        by_mod.setdefault(node["module_name"], []).append(node["callable_name"])
    for mod in sorted(by_mod):
        lines.append(f"- `{mod}`: " + ", ".join(f"`{n}`" for n in sorted(by_mod[mod])))

    ref_by: dict[str, set[str]] = {}
    for edge in edges:
        if edge["callee_qualified_name"]:
            ref_by.setdefault(edge["callee_qualified_name"], set()).add(edge["caller_qualified_name"])

    lines.extend(["", "## 3. Implementation helper index", "", "| Module | Shared/private helper | Called by public callables |", "|---|---|---|"])
    public_qns = {n["qualified_name"] for n in public_nodes}
    for node in helper_nodes:
        qn = node["qualified_name"]
        callers = sorted([x for x in ref_by.get(qn, set()) if x in public_qns])
        lines.append(
            f"| `{node['module_name']}` | `{node['callable_name']}` | "
            f"{', '.join(f'`{x}`' for x in callers) or '—'} |"
        )

    lines.extend(["", "## 4. Cross-module FabricOps calls", "", "| Caller | Callee | Callee kind |", "|---|---|---|"])
    for edge in cross_edges:
        lines.append(
            f"| `{edge['caller_qualified_name']}` | `{edge['callee_qualified_name']}` | `{edge['callee_kind']}` |"
        )

    lines.extend([
        "",
        "## 5. Notes",
        "",
        "Per-function call graph and helper/callee details are generated on each public callable page.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    """Run the command-line workflow."""
    REFERENCE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    generate_metadata_reference_pages()
    public = parse_public_exports()
    module_data = {source_module_name(p): parse_module(p) for p in source_module_paths()}
    if "io.shared" in module_data:
        module_data["io"] = module_data["io.shared"]
    if "config.shared" in module_data:
        module_data["config"] = module_data["config.shared"]

    docs_metadata = parse_docs_metadata()
    usage_note_by_path_prefix, usage_note_by_function = parse_usage_note_metadata()
    template_flow_docs = parse_template_flow_docs()
    # This generator writes individual function pages and the function reference landing page.
    # Module pages, glossary surfaces, manifests, dashboard assets, and JSON data artifacts
    # stay outside this generator output contract.
    missing_metadata = sorted(name for name in public if name not in docs_metadata)
    if missing_metadata:
        raise RuntimeError("Missing PUBLIC_SYMBOL_DOCS entries for __all__ exports: " + ", ".join(missing_metadata))
    invalid_public_exports = sorted(
        name for name in public if str(docs_metadata[name].get("function_type", "")).lower() not in {"callable", "class"}
    )
    if invalid_public_exports:
        raise RuntimeError(
            "__all__ exports must have PUBLIC_SYMBOL_DOCS function_type=callable or function_type=class: "
            + ", ".join(invalid_public_exports)
        )
    # PUBLIC_SYMBOL_DOCS may retain metadata for internalized helpers so generated
    # implementation relationship details remain useful on public parent pages.

    symbol_map: dict[str, Symbol] = {}
    for name in public:
        preferred_module = canonical_public_module(docs_metadata[name]["module"])
        preferred_actual_module = resolve_preferred_actual_module(preferred_module)
        modules_to_check = ([preferred_actual_module] if preferred_actual_module in module_data else []) + [m for m in module_data if m != preferred_actual_module]
        for module in modules_to_check:
            info = module_data[module]
            if name in info["functions"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "function", info["functions"][name])
                break
            if name in info["classes"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "class", info["classes"][name])
                break
            if name in info["constants"]:
                symbol_map[name] = Symbol(name, module, preferred_module, "constant", info["constants"][name])
                break
        if name not in symbol_map:
            raise RuntimeError(f"Could not resolve exported symbol {name} to a module-level function/class.")

    for symbol in symbol_map.values():
        meta = docs_metadata[symbol.name]
        if meta["kind"] != symbol.obj_type:
            raise RuntimeError(f"Metadata kind mismatch for {symbol.name}: expected {symbol.obj_type}, found {meta['kind']}")
        symbol.summary = meta.get("summary_override") or symbol.summary
        symbol.purpose = meta.get("purpose") or symbol.summary or "—"
        enforce_placeholder_guard = symbol.actual_module in {"config", "ai"}
        if enforce_placeholder_guard and symbol.summary:
            _assert_non_placeholder_summary(symbol.name, "summary", symbol.summary)
        if enforce_placeholder_guard and symbol.purpose and symbol.purpose != "—":
            _assert_non_placeholder_summary(symbol.name, "purpose", symbol.purpose)
        symbol_role = meta.get("function_type")
        if not symbol_role:
            raise RuntimeError(f"Missing explicit function_type for {symbol.name} in PUBLIC_SYMBOL_DOCS")
        symbol.role = str(symbol_role).lower()
        if symbol.role not in {"callable", "class", "internal"}:
            raise RuntimeError(f"Invalid function type {symbol.role!r} for {symbol.name}; expected callable/class/internal")
        if symbol.role == "internal" and not symbol.name.startswith("_"):
            raise RuntimeError(f"Non-underscore callable cannot be internal: {symbol.name}")
        if symbol.role == "callable" and symbol.name.startswith("_"):
            raise RuntimeError(f"Underscore callable cannot be public callable: {symbol.name}")

    core_template_usage_by_symbol, example_template_usage_by_symbol, imported_only_by_symbol = _derive_template_usage_by_kind(template_flow_docs, symbol_map)
    template_usage_by_symbol = {
        name: [*core_template_usage_by_symbol.get(name, []), *example_template_usage_by_symbol.get(name, [])]
        for name in symbol_map
    }
    nodes, edges, module_summary = build_callable_graph(module_data, symbol_map, public, docs_metadata)
    node_by_qn = {n["qualified_name"]: n for n in nodes}
    calls_by_qn: dict[str, list[str]] = {}
    used_by_qn: dict[str, list[str]] = {}
    for e in edges:
        caller = e["caller_qualified_name"]
        callee = e.get("callee_qualified_name")
        if not callee:
            continue
        calls_by_qn.setdefault(caller, []).append(callee)
        used_by_qn.setdefault(callee, []).append(caller)

    template_paths_in_metadata = {flow.get("template_path") for flow in template_flow_docs}
    missing_template_paths = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "templates" / "notebooks").glob("*.ipynb")
        if path.relative_to(ROOT).as_posix() not in template_paths_in_metadata
    )
    if missing_template_paths:
        missing = ", ".join(missing_template_paths)
        raise RuntimeError(f"TEMPLATE_FLOW_DOCS is missing notebook templates: {missing}")

    public_symbol_names = set(symbol_map)
    for flow in template_flow_docs:
        expected_symbols = [
            symbol
            for segment in flow["segments"]
            for symbol in segment["symbols"]
        ]
        actual_symbols = _direct_public_template_symbols(flow.get("template_path", ""), public_symbol_names)
        if set(expected_symbols) != set(actual_symbols):
            expected = ", ".join(sorted(expected_symbols)) or "(none)"
            actual = ", ".join(actual_symbols) or "(none)"
            raise RuntimeError(
                "TEMPLATE_FLOW_DOCS symbols must match direct public callable usage in "
                f"{flow.get('template_path')}: expected metadata [{expected}], actual notebook calls [{actual}]"
            )
    starter_symbol_to_notebooks: dict[str, set[str]] = {}
    for flow in template_flow_docs:
        notebook_key = flow["notebook_key"]
        for segment in flow["segments"]:
            for symbol in segment["symbols"]:
                if symbol not in symbol_map:
                    raise RuntimeError(f"TEMPLATE_FLOW_DOCS references unknown symbol: {symbol}")
                starter_symbol_to_notebooks.setdefault(symbol, set()).add(notebook_key)

    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _html_table(
        table_class: str,
        headers: list[str],
        rows: list[list[str]],
        *,
        row_attrs: list[dict[str, str]] | None = None,
    ) -> list[str]:
        lines = [f'<table class="{table_class}">', "  <thead>", "    <tr>"]
        for header in headers:
            lines.append(f"      <th>{_esc(header)}</th>")
        lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
        for row_index, row in enumerate(rows):
            attr_text = ""
            if row_attrs and row_index < len(row_attrs):
                attrs = row_attrs[row_index]
                attr_text = "".join(f' {key}="{_esc(value)}"' for key, value in attrs.items())
            lines.append(f"    <tr{attr_text}>")
            for idx, cell in enumerate(row):
                lines.append(f'      <td data-label="{_esc(headers[idx])}">{cell}</td>')
            lines.append("    </tr>")
        lines.extend(["  </tbody>", "</table>"])
        return lines

    def _anchor(href: str, text: str, *, code: bool = False) -> str:
        content = f"<code>{_esc(text)}</code>" if code else _esc(text)
        return f'<a href="{_esc(href)}">{content}</a>'

    dashboard_inventory_data = _load_public_call_flow_inventory()
    dashboard_public_functions = sorted(
        dashboard_inventory_data["public_functions"],
        key=lambda row: str(row.get("function_name", "")).lower(),
    )
    public_flow_by_qn = {str(row["qualified_name"]): row for row in dashboard_public_functions}
    public_flow_by_name = {str(row["function_name"]): row for row in dashboard_public_functions}
    node_by_public_function_name = {
        node["callable_name"]: node
        for node in node_by_qn.values()
        if node.get("exported") and node.get("callable_kind") == "function"
    }
    missing_public_flows = sorted(
        f"{PACKAGE_NAME}.{node['module_name']}.{node['callable_name']}"
        for node in node_by_public_function_name.values()
        if f"{PACKAGE_NAME}.{node['module_name']}.{node['callable_name']}" not in public_flow_by_qn
    )
    if missing_public_flows:
        raise RuntimeError(
            "Public function reference lifecycle data missing for:\n"
            + "\n".join(missing_public_flows)
        )
    public_function_count = len(dashboard_public_functions)
    callable_metrics = {
        "public_api_entrypoints": public_function_count,
        "module_count": len([m for m in module_data if m != "docs_metadata"]),
        "total_callables": len(node_by_qn),
        "supporting_functions": len([n for n in node_by_qn.values() if not n.get("exported") and not str(n.get("callable_name", "")).startswith("_")]),
        "hidden_private_helpers": len([n for n in node_by_qn.values() if str(n.get("callable_name", "")).startswith("_")]),
    }
    ref = [
        "# Function Reference",
        "",
        "Use this page to look up public notebook-facing Starter Kit functions used by the template notebooks.",
        "",
        '<div class="reference-kpi-grid" aria-label="Function reference summary">',
        '  <section class="reference-kpi-card surface-card">',
        f'    <strong class="reference-kpi-value">{callable_metrics["public_api_entrypoints"]}</strong>',
        '    <span class="reference-kpi-title">Public functions</span>',
        '    <p class="reference-kpi-note">Notebook-facing Starter Kit functions.</p>',
        '  </section>',
        '</div>',
        "",
        "<p><small>Function metrics are generated from the runtime inventory data.</small></p>",
        "",
    ]

    ref.extend(
        [
            "## Find a function",
            "",
            f"Use the finder below to search {public_function_count} public functions. Config classes stay out of the Function Reference and can be documented later in a separate schema/config reference. “Used in” means direct starter notebook code-cell invocation, not import-only, markdown-only, generated metadata, example usage, or implementation helper usage.",
            "",
            '<div class="callable-finder" data-callable-finder>',
            '  <label class="callable-finder-label" for="callable-finder-input">Search public functions</label>',
            '  <input id="callable-finder-input" class="callable-finder-input" type="search" placeholder="Search public functions" aria-describedby="callable-finder-help callable-finder-status callable-finder-examples" autocomplete="off">',
            '  <p id="callable-finder-help" class="callable-finder-help">Search by function name, module, starter path, usage source, or description.</p>',
            '  <p id="callable-finder-examples" class="callable-finder-examples">Try: <span class="callable-finder-chip">dq_rules</span> <span class="callable-finder-chip">lineage</span> <span class="callable-finder-chip">guardrail</span></p>',
            f'  <p id="callable-finder-status" class="callable-finder-status" aria-live="polite">Showing {public_function_count} public functions.</p>',
            '  <p class="callable-finder-empty" data-callable-finder-empty hidden>No public functions match your search.</p>',
            "</div>",
            "",
            '??? info "Maintainer tools"',
            '    Use these links and notes when maintaining the reference system.',
            '',
            '    Maintainer inventory metrics:',
            '',
            f'    - Source Python files count: {callable_metrics["module_count"]}',
            f'    - Total callables: {callable_metrics["total_callables"]}',
            f'    - Supporting functions: {callable_metrics["supporting_functions"]}',
            f'    - Private helpers to review: {callable_metrics["hidden_private_helpers"]}',
            '',
            '    - [Function Call Graph](../function-call-graph.md): explanatory page for the v2 public-function call-flow architecture contract.',
            '    - [public-function-call-flows.json](_data/public-function-call-flows.json): v2 architecture contract generated by `scripts/generate_public_function_call_flows_json.py`.',
            '    - [Public function call-flow dashboard](../assets/public-function-call-flows-dashboard.html): frontend generated by `scripts/generate_public_function_call_flows_dashboard.py`.',
            '    - Implementation contracts: expectations maintainers must satisfy before using or changing a function.',
            '    - Skill file: `.agents/skills/fabricops/SKILL.md`.',
            '',
            "## Function catalogue",
            "",
            "## Public functions",
            "",
        ]
    )
    all_items: list[str] = []
    catalogue_nodes = [node_by_public_function_name[row["function_name"]] for row in dashboard_public_functions if row["function_name"] in node_by_public_function_name]
    for node in catalogue_nodes:
        name = node["callable_name"]
        module_name = node["module_name"]
        function_type = "public-starter-kit"
        symbol = symbol_map[name]
        symbol_link = public_reference_link(name, docs_metadata, context="reference")
        starter_path = ", ".join(core_template_usage_by_symbol.get(name, [])) or "—"
        usage_source = ", ".join(template_usage_by_symbol.get(name, [])) or "—"
        purpose = symbol.purpose or symbol.summary or "—"
        display_module = symbol.public_module
        starter_path_attribute = f' data-callable-starter-path="{_esc(starter_path)}"' if starter_path != "—" else ""
        usage_source_attribute = f' data-callable-usage-source="{_esc(usage_source)}"' if usage_source != "—" else ""
        qn = f"{PACKAGE_NAME}.{module_name}.{name}"
        public_flow = public_flow_by_qn[qn]
        lifecycle_status = _lifecycle_status(public_flow)
        live_since = _dash(public_flow.get("live_since"))
        lifecycle_extra_chip = ""
        if lifecycle_status == "Live" and live_since != "—":
            lifecycle_extra_chip = _lifecycle_chip(lifecycle_status, f"Live since {live_since}")
        elif lifecycle_status == "Discontinued" and public_flow.get("discontinued_in"):
            lifecycle_extra_chip = _lifecycle_chip(lifecycle_status, f"Discontinued in {public_flow['discontinued_in']}")
        downstream_callables = [row["qualified_name"] for row in public_flow.get("flow", [])[1:] if row.get("qualified_name")]

        def _catalogue_relationship_list(items: list[str]) -> str:
            rows = []
            for item in items:
                related_node = node_by_qn.get(item, {})
                short = related_node.get("callable_name") or item.split(".")[-1]
                if related_node.get("exported"):
                    href = public_reference_link(short, docs_metadata, context="reference")
                    rows.append(f'<li><a href="{_esc(href)}"><code>{_esc(short)}</code></a></li>')
                else:
                    rows.append(f'<li><code>{_esc(short)}</code></li>')
            return "<ul>" + "".join(rows) + "</ul>"

        def _catalogue_count_details(singular_label: str, plural_label: str, items: list[str]) -> str:
            count = len(items)
            if count == 0:
                return ""
            label = singular_label if count == 1 else plural_label
            return (
                '    <details class="reference-count-details"><summary>'
                f'<span class="reference-chip reference-chip-count">{_esc(label.format(count=count))}</span>'
                "</summary>"
                + _catalogue_relationship_list(items)
                + "</details>"
            )

        all_items.extend(
            [
                (
                    f'<article id="{_esc(module_name)}-{_esc(name)}" class="reference-catalogue-item" '
                    f'data-callable-row="true" data-callable-name="{_esc(name)}" '
                    f'data-callable-module="{_esc(display_module)}"'
                    f'{starter_path_attribute}'
                    f'{usage_source_attribute} '
                    f'data-function-type="{_esc(function_type)}" '
                    f'data-callable-purpose="{_esc(purpose)}">'
                ),
                f'  <h3 class="reference-catalogue-item-name"><a class="reference-catalogue-item-title" href="{_esc(symbol_link)}"><code>{_esc(name)}</code></a></h3>',
                f'  <p class="reference-catalogue-item-purpose">{_esc(purpose)}</p>',
                (
                    '  <p class="reference-catalogue-item-meta reference-catalogue-item-badges">'
                    f'{_lifecycle_chip(lifecycle_status, prominent=True)}'
                    f'{lifecycle_extra_chip}'
                    f'<span class="reference-chip reference-chip-muted">{_esc("Public function")}</span>'
                    f'<span class="reference-chip">{_esc(usage_source)}</span>'
                    "</p>"
                ),
                (
                    f'  <p class="reference-catalogue-item-used-in"><strong>Used in notebooks:</strong> {_esc(usage_source)}</p>'
                    if usage_source != "—"
                    else ""
                ),
                '  <p class="reference-catalogue-item-provenance">Dependency data is generated from the callable architecture inventory.</p>',
                '  <div class="reference-catalogue-item-counts">',
                _catalogue_count_details("Downstream callables: {count}", "Downstream callables: {count}", downstream_callables),
                "  </div>",
                "</article>",
            ]
        )
    table_lines = [
        "| Function | Lifecycle | Live since | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for node in catalogue_nodes:
        name = node["callable_name"]
        symbol = symbol_map[name]
        qn = f"{PACKAGE_NAME}.{node['module_name']}.{name}"
        public_flow = public_flow_by_qn[qn]
        status = _lifecycle_status(public_flow)
        purpose = symbol.purpose or symbol.summary or "—"
        table_lines.append(
            f"| [`{_esc(name)}`]({public_reference_link(name, docs_metadata, context='reference')}) "
            f"| {_lifecycle_chip(status)} | {_dash(public_flow.get('live_since'))} | {_esc(purpose)} |"
        )
    ref.extend([*table_lines, "", '<div class="reference-catalogue-list">', *all_items, "</div>"])

    ref.append("")
    REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_PATH.write_text("\n".join(ref) + "\n", encoding="utf-8", newline="\n")

    generate_internal_pages = generate_internal_reference_pages()
    CALLABLE_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    # Legacy callable pages are outside this generator's output contract.
    # Internal reference pages are outside this generator's output contract.
    for generated_page in CALLABLE_REFERENCE_DIR.glob("*.md"):
        generated_page.unlink(missing_ok=True)
    update_generated_artifact_metadata(
        artifact_key="individual_function_reference_pages",
        label="Individual function reference pages",
        generator="scripts/generate_individual_function_reference_pages.py",
        output_path="docs/api/reference",
    )
    for public_flow in dashboard_public_functions:
        short_name = str(public_flow["function_name"])
        node = node_by_public_function_name.get(short_name)
        if not node:
            continue
        qn = str(public_flow["qualified_name"])
        lifecycle_status = _lifecycle_status(public_flow)
        module_name = node["module_name"]
        raw_deps = sorted(set(calls_by_qn.get(qn, [])))
        raw_used_by = sorted(set(used_by_qn.get(qn, [])))
        deps = [d for d in raw_deps if not _hide_from_public_relationships(d)] if node["exported"] else raw_deps
        used_by = [u for u in raw_used_by if not _hide_from_public_relationships(u)] if node["exported"] else raw_used_by
        metadata = docs_metadata.get(short_name, {})
        module_info = module_data[module_name]
        doc_intro = module_info.get("doc_intro", {}).get(short_name, "")
        doc_sections = module_info.get("doc_sections", {}).get(short_name, {})
        signature = module_info.get("signatures", {}).get(short_name, "")
        summary = metadata.get("summary_override") or ""
        source_path = module_info.get("source_path") or f"src/fabricops_kit/{module_name.replace('.', '/')}.py"
        source_location = module_info.get("source_locations", {}).get(short_name, {})
        source_start_line = source_location.get("start_line")
        source_end_line = source_location.get("end_line")
        source_ref = github_source_url(source_path, source_start_line, source_end_line)
        parameter_rows = module_info.get("parameters", {}).get(short_name, [])
        purpose = summary or module_info["functions"].get(short_name) or module_info["classes"].get(short_name) or "No summary available."
        rendered_returns = _documented_text(metadata.get("returns"), doc_sections.get("returns"))
        rendered_return_interpretation = _documented_text(metadata.get("return_interpretation"))
        rendered_raises = _documented_text(metadata.get("raises"), doc_sections.get("raises"))
        rendered_common_failure_causes = _documented_text(metadata.get("common_failure_causes"))
        rendered_side_effects = _documented_text(metadata.get("side_effects"))
        def _fmt_links(items: list[str]) -> list[str]:
            out = []
            for item in items:
                n = node_by_qn.get(item, {})
                if not n:
                    continue
                if n.get("exported"):
                    href = f"{n['callable_name']}/"
                    out.append(f'- <a href="{href}"><code>{item}</code></a>')
                elif n.get("callable_name", "").startswith("_") and generate_internal_reference_pages():
                    href = f"../internal/{n['module_name']}_{n['callable_name']}/"
                    out.append(f'- <a href="{href}"><code>{item}</code></a>')
                else:
                    out.append(f"- `{item}`")
            return out

        if node["exported"]:
            parameter_overrides = _metadata_parameter_overrides(metadata.get("parameters"))
            input_lines = _render_parameter_definitions(parameter_rows, parameter_overrides, PARAMETER_DISPLAY_TYPES.get(short_name, {}))
            public_flow = public_flow_by_name.get(short_name, public_flow_by_qn[qn])
            lifecycle_status = _lifecycle_status(public_flow)
            used_in_templates = template_usage_by_symbol.get(short_name, [])
            downstream_count = len(public_flow.get("flow", [])) - 1
            shared_helper_count = sum(1 for row in public_flow.get("flow", [])[1:] if row.get("function_type") == "shared_function")
            private_helper_count = sum(1 for row in public_flow.get("flow", [])[1:] if row.get("function_type") == "private_function")
            dashboard_url = _dashboard_focus_url(short_name)
            call_flow_lines = [
                "## Call-flow summary",
                "",
                f"- Downstream callables: {downstream_count}",
                f"- Shared helpers: {shared_helper_count}",
                f"- Private helpers: {private_helper_count}",
                "",
                f'<a class="reference-source-link" href="{dashboard_url}">{html_escape(_dashboard_link_label(lifecycle_status))}</a>',
                "",
            ]
            notebook_usage_chips = [
                f'<span class="reference-chip">{html_escape(template)}</span>' for template in used_in_templates
            ] or ['<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>']
            page_chip_lines = [
                '<p class="reference-catalogue-item-meta reference-catalogue-item-badges">',
                '<span class="reference-chip">Public Starter Kit function</span>',
                *notebook_usage_chips,
                '</p>',
            ]
            usage_notes = _usage_notes_for_public_function(
                function_name=short_name,
                source_path=source_path,
                metadata=metadata,
                usage_note_by_path_prefix=usage_note_by_path_prefix,
                usage_note_by_function=usage_note_by_function,
            )
            doc_intro_lines = (
                [*_reference_markdown_block(doc_intro, class_name="reference-docstring-intro"), ""]
                if doc_intro
                else []
            )
            notes_lines = (
                ["## Notes", "", *_reference_markdown_block(doc_sections.get("notes", ""), class_name="reference-docstring-notes"), ""]
                if doc_sections.get("notes", "")
                else []
            )
            usage_guidance_lines = ["## Usage notes", "", usage_notes, ""] if usage_notes else []
            related_guide_lines = _render_related_guides(list(metadata.get("related_guides", [])))
            see_also_lines = related_guide_lines if related_guide_lines else ["## See also", "", "No related guides documented.", ""]
            rendered_example_usage = _render_example_usage(
                short_name,
                signature,
                metadata,
                doc_sections.get("examples", ""),
            )
            return_interpretation_lines = (
                ["### Return interpretation", "", rendered_return_interpretation, ""]
                if metadata.get("return_interpretation")
                else []
            )
            common_failure_cause_lines = (
                ["### Common failure causes", "", rendered_common_failure_causes, ""]
                if metadata.get("common_failure_causes")
                else []
            )
            lines = [
                f"# `{short_name}`",
                "",
                *_lifecycle_header_lines(public_flow),
                *call_flow_lines,
                purpose,
                "",
                *doc_intro_lines,
                *_source_card_lines(source_path=source_path, source_start_line=source_start_line, source_ref=source_ref, short_name=short_name),
                "",
                *page_chip_lines,
                "",
                "**Used in notebooks:** "
                + (
                    ", ".join(f"`{template}`" for template in used_in_templates)
                    if used_in_templates
                    else "Usage detection may exclude indirect or generated references."
                ),
                "",
                *usage_guidance_lines,
                "",
                "## Signature",
                "",
                *_reference_code_block(_format_api_signature(signature), class_name="reference-api-definition"),
                "",
                *(
                    [
                        "## Example usage",
                        "",
                        *rendered_example_usage,
                        "",
                    ]
                ),
                "## Parameters",
                "",
                *input_lines,
                "",
                "## Returns",
                "",
                rendered_returns,
                "",
                *return_interpretation_lines,
                "## Raises / Errors",
                "",
                rendered_raises,
                "",
                *common_failure_cause_lines,
                *notes_lines,
                *see_also_lines,
            ]
        else:
            lines = [
                f"# {short_name}",
                "",
                f"**Module:** `{module_name}`",
                "**Layer:** Internal",
                "",
                "## Status",
                "",
                "Implementation helper used by the package implementation.",
                "",
                "## Function type: Shared helper",
                "",
                "Shared helper",
                "",
                "## Direct use: No",
                "",
                "Do not call this helper directly from notebooks; use the public callable helpers instead.",
                "",
                "## Used by",
                "",
            ]
            lines.extend(_fmt_links(used_by) if used_by else [PLACEHOLDER])
            lines.extend([
                "",
                "## Purpose",
                "",
                purpose,
                "",
                "## Signature if available",
                "",
                _code_block(_format_api_signature(signature)) if signature else PLACEHOLDER,
                "",
                "## Side effects",
                "",
                rendered_side_effects,
                "",
                "## Maintainer notes",
                "",
                "Maintain this helper through the owning implementation module and keep generated references in sync.",
                "",
                "## Implementation contract",
                "",
                _documented_text(metadata.get("ai_verification"), "Use internal pages only for package maintenance. Prefer public callable pages when authoring notebooks."),
                "",
            ])

        if not node["exported"]:
            if used_by:
                lines.extend(["", "## Used by references", *(_fmt_links(used_by))])
            if deps:
                lines.extend(["", "## Calls references", *(_fmt_links(deps))])
            if not used_by and not deps:
                lines.extend(["", "_No used-by or calls references detected._"])

        if node["exported"]:
            lines.extend(["", "<details>", "<summary>Maintainer architecture details</summary>", "", *_contract_impact_lines(public_flow, docs_metadata=docs_metadata, public_page_names=set(public_flow_by_name)), "", "</details>"])
            lines.extend(_generated_freshness_note())
            (CALLABLE_REFERENCE_DIR / f"{short_name}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        elif generate_internal_pages:
            pass


if __name__ == "__main__":
    main()
