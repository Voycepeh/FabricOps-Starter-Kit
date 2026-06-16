# widget_author_guardrail_rules

Render clear guardrail authoring widgets for the selected table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2775`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2775-L2806">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after target selection when governance users need to create guardrail rule records before review.

**Do not use when:**

- Do not use for formal approve, reject, replace, or deactivate decisions; use widget_review_table_governance.

**Additional context:**

Groups guardrail authoring controls so governance notebooks can author rules separately from formal review decisions.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_guardrail_rules(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. |
| `config` | `Any` | No | Runtime configuration used for metadata writes. |
| `env` | `str \| None` | No | Environment key used to route metadata writes. |
| `spark_session` | `Any` | No | Spark session used to append authored rule records. |

## Returns

Nested notebook-facing state for schema/freshness/profile and DQ authoring widgets.

### Return interpretation

The returned dictionary contains the nested authoring widget states and save helpers.

## Raises / Errors

Not documented yet

### Common failure causes

- No target state is selected.
- The selected table has no columns.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- <a href="../widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="../widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    ```text
    widget_author_guardrail_rules(...)
    ├── widget_author_dq_rules(...)
    │   ├── _dq_records_from_selection(...)
    │   │   └── _base_guardrail_rule_record(...)
    │   │       ├── _build_dq_rule_key(...)
    │   │       │   └── _stable_metadata_key(...)
    │   │       ├── _build_metadata_column_key(...)
    │   │       │   └── _stable_metadata_key(...)
    │   │       ├── _build_metadata_table_key(...)
    │   │       │   └── _stable_metadata_key(...)
    │   │       ├── _now_utc_iso(...)
    │   │       │   └── _current_audit_timestamp(...)
    │   │       │       └── _get_audit_timezone(...)
    │   │       │           └── …
    │   │       ├── _resolve_action_by(...)
    │   │       │   ├── _context_get(...)
    │   │       │   └── _runtime_context(...)
    │   │       │       └── _context_get(...)
    │   │       └── guardrail_authoring_status(...)
    │   │           ├── _authoring_lifecycle(...)
    │   │           │   └── _activation_fields(...)
    │   │           │       └── …
    │   │           ├── _now_utc_iso(...)
    │   │           │   └── _current_audit_timestamp(...)
    │   │           │       └── …
    │   │           └── _resolve_action_by(...)
    │   │               ├── _context_get(...)
    │   │               └── _runtime_context(...)
    │   │                   └── …
    │   ├── _draft_dq_rules(...)
    │   │   ├── _canonical_dq_rule_type(...)
    │   │   ├── _extract_assignment_payload(...)
    │   │   │   ├── _coerce_rows(...)
    │   │   │   └── _parse_ai_dict_response(...)
    │   │   ├── _prepare_dq_profile_input_rows(...)
    │   │   │   ├── _current_audit_timestamp(...)
    │   │   │   │   └── _get_audit_timezone(...)
    │   │   │   │       └── _validate_audit_timezone(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── profile_dataframe(...)
    │   │   │       ├── _audit_timestamp_expr(...)
    │   │   │       │   └── _get_audit_timezone(...)
    │   │   │       │       └── …
    │   │   │       ├── _build_distribution_summaries(...)
    │   │   │       │   ├── _build_categorical_distribution(...)
    │   │   │       │   ├── _build_numeric_distribution(...)
    │   │   │       │   └── _numeric_bin_edges(...)
    │   │   │       ├── _get_audit_timezone(...)
    │   │   │       │   └── _validate_audit_timezone(...)
    │   │   │       ├── _get_profiled_columns(...)
    │   │   │       └── _is_min_max_supported_type(...)
    │   │   ├── _run_fabric_ai_drafting(...)
    │   │   └── _validate_dq_rules(...)
    │   │       ├── _canonical_dq_rule_type(...)
    │   │       └── _normalize_dq_severity(...)
    │   ├── _latest_rule(...)
    │   ├── _rule_params(...)
    │   └── _write_rule_records(...)
    │       ├── _configured_lakehouse_schema(...)
    │       │   ├── _get_store(...)
    │       │   │   └── _normalize_path_config(...)
    │       │   │       └── PathConfig(...)
    │       │   └── _normalize_schema_name(...)
    │       └── write_lakehouse_table(...)
    │           ├── _get_store(...)
    │           │   └── _normalize_path_config(...)
    │           │       └── PathConfig(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_table_path(...)
    │               ├── _normalize_table_name(...)
    │               └── _resolve_lakehouse_schema(...)
    │                   └── _normalize_schema_name(...)
    └── widget_author_schema_freshness_profile_rules(...)
        ├── _latest_rule(...)
        ├── _rule_params(...)
        ├── _schema_freshness_profile_records_from_selection(...)
        │   └── _base_guardrail_rule_record(...)
        │       ├── _build_dq_rule_key(...)
        │       │   └── _stable_metadata_key(...)
        │       ├── _build_metadata_column_key(...)
        │       │   └── _stable_metadata_key(...)
        │       ├── _build_metadata_table_key(...)
        │       │   └── _stable_metadata_key(...)
        │       ├── _now_utc_iso(...)
        │       │   └── _current_audit_timestamp(...)
        │       │       └── _get_audit_timezone(...)
        │       │           └── …
        │       ├── _resolve_action_by(...)
        │       │   ├── _context_get(...)
        │       │   └── _runtime_context(...)
        │       │       └── _context_get(...)
        │       └── guardrail_authoring_status(...)
        │           ├── _authoring_lifecycle(...)
        │           │   └── _activation_fields(...)
        │           │       └── …
        │           ├── _now_utc_iso(...)
        │           │   └── _current_audit_timestamp(...)
        │           │       └── …
        │           └── _resolve_action_by(...)
        │               ├── _context_get(...)
        │               └── _runtime_context(...)
        │                   └── …
        └── _write_rule_records(...)
            ├── _configured_lakehouse_schema(...)
            │   ├── _get_store(...)
            │   │   └── _normalize_path_config(...)
            │   │       └── PathConfig(...)
            │   └── _normalize_schema_name(...)
            └── write_lakehouse_table(...)
                ├── _get_store(...)
                │   └── _normalize_path_config(...)
                │       └── PathConfig(...)
                ├── _normalize_table_name(...)
                └── _resolve_lakehouse_table_path(...)
                    ├── _normalize_table_name(...)
                    └── _resolve_lakehouse_schema(...)
                        └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 0"

    This callable uses 0 internal helpers; `widget_author_guardrail_rules` does not have package-local helper descendants in the generated call graph.

    <div class="reference-helper-groups">
      <section class="reference-helper-group reference-helper-group-empty">
        <h4>No internal helpers detected</h4>
        <p>This callable does not have package-local helper descendants in the generated call graph.</p>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_author_guardrail_rules`
- Short name: `widget_author_guardrail_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2775`
- Inbound references count: 0
- Outbound references count: 2
- Used in templates: 03_governance
- Glossary terms: guardrail, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Nested notebook-facing state for schema/freshness/profile and DQ authoring widgets.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="../widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2775-L2806">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/12722d7550847cd70c6e1ef934f6b6269f02d2f7/src/fabricops_kit/governance_review.py#L2775-L2806</a>
- Start line: `2775`
- End line: `2806`
- Signature:

```python
def widget_author_guardrail_rules(
    state: Mapping[str, Any],
    config: Any=None,
    env: str | None=None,
    spark_session: Any=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../widget_author_schema_freshness_profile_rules/"><code>fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules</code></a>
- <a href="../widget_author_dq_rules/"><code>fabricops_kit.governance_review.widget_author_dq_rules</code></a>
- <a href="../widget_review_table_governance/"><code>fabricops_kit.governance_review.widget_review_table_governance</code></a>

### Internal implementation summary

- Internal helper count: 0
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
