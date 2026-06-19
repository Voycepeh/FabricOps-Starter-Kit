# widget_author_schema_freshness_profile_rules

Render interactive schema, freshness, and profile-behavior guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:2252`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 02_pipeline after selecting a guardrail target to save active self-approved rules, submit proposed rules, or bypass approval with a required reason.

### Do not use when

- Do not use to write evidence or runtime outcomes; it writes rule intent only to METADATA_GUARDRAIL_RULES when saving.

### Additional context

Renders interactive controls for authoring schema, freshness, and profile-behavior guardrail rule intent while applying the selected table governance policy.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Handover state from :func:`widget_select_guardrail_target`. |
| `spark_session` | `Any` | No | Spark session used for save actions. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `bypass_reason` | `str` | No | Initial approval-bypass reason. |
| `source_notebook_type` | `str` | No | Notebook type stamped on authored records. |
| `created_by_role` | `str` | No | Role stamped on authored records. |
| `commit` | `bool` | No | Whether to save the initial generated records immediately. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget state exposes controls, preview records, and save actions that produce append-only guardrail rule rows under the table policy.

## Raises / Errors

Not documented yet

### Common failure causes

- The handover state is missing columns.
- Changing-data profile behavior has no watermark column.
- Freshness max lag is invalid.
- The metadata target cannot be written.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._schema_freshness_profile_records_from_selection`
- `fabricops_kit.governance_review._write_rule_records`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`
- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

No additional callable notes are documented.

</details>

??? info "Call flow"

    Unique internal helpers: 26. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>widget_author_schema_freshness_profile_rules(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2060-L2073"><code>_latest_rule(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2076-L2082"><code>_rule_params(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2182-L2249"><code>_schema_freshness_profile_records_from_selection(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1808-L1840"><code>guardrail_authoring_status(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1764-L1766"><code>_is_no_approval_required(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1775-L1791"><code>_lifecycle_fields(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   │           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           │           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1764-L1766"><code>_is_no_approval_required(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L438-L548"><code>write_lakehouse_table(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L225-L246"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│           └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

    ### Refactor signals

    These generated hints point maintainers to call-tree shapes worth reviewing; they are not automatic refactor requirements.

    **Helpers appearing in multiple branches**

    - `_context_get` appears in 4 branches.
    - `_stable_metadata_key` appears in 3 branches.
    - `_current_audit_timestamp` appears in 2 branches.
    - `_get_audit_timezone` appears in 2 branches.
    - `_get_store` appears in 2 branches.
    - `_is_no_approval_required` appears in 2 branches.
    - `_normalize_path_config` appears in 2 branches.
    - `_normalize_schema_name` appears in 2 branches.
    - `_normalize_table_name` appears in 2 branches.
    - `_now_utc_iso` appears in 2 branches.
    - `_resolve_action_by` appears in 2 branches.
    - `_runtime_context` appears in 2 branches.

    **Call chains deeper than 4 levels**

    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `_now_utc_iso` → `_current_audit_timestamp` → `_get_audit_timezone`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `_now_utc_iso` → `_current_audit_timestamp` → `_get_audit_timezone` → `_validate_audit_timezone`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `_resolve_action_by` → `_runtime_context` → `_context_get`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `guardrail_authoring_status` → `_authoring_lifecycle` → `_is_no_approval_required`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `guardrail_authoring_status` → `_authoring_lifecycle` → `_lifecycle_fields`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `guardrail_authoring_status` → `_authoring_lifecycle` → `_now_utc_iso`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `guardrail_authoring_status` → `_authoring_lifecycle` → `_now_utc_iso` → `_current_audit_timestamp`
    - `widget_author_schema_freshness_profile_rules` → `_schema_freshness_profile_records_from_selection` → `_base_guardrail_rule_record` → `guardrail_authoring_status` → `_authoring_lifecycle` → `_now_utc_iso` → `_current_audit_timestamp` → `_get_audit_timezone`

    **Helpers that only call one package-local helper**

    - `_current_audit_timestamp` only delegates to `_get_audit_timezone`.
    - `_get_audit_timezone` only delegates to `_validate_audit_timezone`.
    - `_get_store` only delegates to `_normalize_path_config`.
    - `_resolve_lakehouse_schema` only delegates to `_normalize_schema_name`.
    - `_schema_freshness_profile_records_from_selection` only delegates to `_base_guardrail_rule_record`.
    - `_build_dq_rule_key` only delegates to `_stable_metadata_key`.
    - `_build_metadata_column_key` only delegates to `_stable_metadata_key`.
    - `_build_metadata_table_key` only delegates to `_stable_metadata_key`.
    - `_now_utc_iso` only delegates to `_current_audit_timestamp`.
    - `_runtime_context` only delegates to `_context_get`.

    **Helpers grouped into possibly wrong areas**

    - None detected from helper names, doc summaries, and module placement.

This callable uses 26 internal helpers for audit timestamp, metadata loading, validation, rule parsing, rule evaluation, fabric or spark access, and other.

<div class="reference-helper-groups">
  <section class="reference-helper-group">
    <h4>Audit timestamp</h4>
    <p>Resolve and stamp audit time consistently.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Metadata loading</h4>
    <p>Load and identify the metadata or table context needed by the callable.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2006-L2023"><code>_base_guardrail_rule_record</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2085-L2096"><code>_write_rule_records</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Validation</h4>
    <p>Validate inputs and guard conditions before the workflow continues.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1764-L1766"><code>_is_no_approval_required</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Rule parsing</h4>
    <p>Normalize stored or user-provided values before applying rules.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2076-L2082"><code>_rule_params</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Rule evaluation</h4>
    <p>Convert configured rules into executable checks and evaluation results.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L138-L139"><code>_build_dq_rule_key</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2060-L2073"><code>_latest_rule</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2182-L2249"><code>_schema_freshness_profile_records_from_selection</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Fabric or Spark access</h4>
    <p>Access Fabric or Spark runtime services used by the implementation.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>
    </div>
  </section>
  <section class="reference-helper-group">
    <h4>Other</h4>
    <p>Support lower-level implementation details that do not fit the main helper areas.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1794-L1806"><code>_authoring_lifecycle</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1775-L1791"><code>_lifecycle_fields</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
    </div>
  </section>
</div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_author_schema_freshness_profile_rules`
- Short name: `widget_author_schema_freshness_profile_rules`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `2252`
- Inbound references count: 0
- Outbound references count: 5
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: guardrails, profile behavior, metadata lakehouse, notebook template

### Implementation contract

- **required_context:** Starter template: `02_pipeline`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._latest_rule`
- `fabricops_kit.governance_review._rule_params`
- `fabricops_kit.governance_review._schema_freshness_profile_records_from_selection`
- `fabricops_kit.governance_review._write_rule_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L2252-L2397</a>
- Start line: `2252`
- End line: `2397`
- Signature:

```python
def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 26
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Profile mode</span><span class="glossary-chip-definition">Configured behavior mode for profile guardrails: static_data, changing_data, or skip.</span> <a href="../../../reference/glossary/#profile-mode">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
