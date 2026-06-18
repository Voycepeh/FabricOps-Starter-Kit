# widget_enrich_table_metadata

Render a consolidated column enrichment widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:642`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L642-L776">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.

### Do not use when

- Do not use to author DQ rules or enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.

### Additional context

Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profiles.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    spark_session: Any,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `guardrail_state` | `Mapping[str, Any]` | Yes | Target handover state returned by :func:`widget_select_guardrail_target`. |
| `spark_session` | `Any` | Yes | Spark session used to create write DataFrames. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `source_notebook_type` | `str` | No | Notebook type stamped on authored records. |
| `created_by_role` | `str` | No | Role stamped on authored records. |

## Returns

Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.

### Return interpretation

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- The selected guardrail target has no column-level evidence.
- Configured custom fields omit a field name.
- Metadata lakehouse writes cannot be routed through 00_env_config.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._collect_enrichment_extra_fields`
- `fabricops_kit.governance_review._enrichment_options`
- `fabricops_kit.governance_review._render_enrichment_extra_fields`
- `fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.governance_review._write_table_metadata_enrichment_records`
- `fabricops_kit.governance_review.build_enrichment_rule_records`

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

    ```text
    widget_enrich_table_metadata(...)
    ├── _collect_enrichment_extra_fields(...)
    ├── _enrichment_options(...)
    ├── _render_enrichment_extra_fields(...)
    ├── _selected_catalogue_rows_for_enrichment(...)
    │   └── _value(...)
    ├── _value(...)
    ├── _write_table_metadata_enrichment_records(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   └── _normalize_schema_name(...)
    │   └── write_lakehouse_table(...)
    │       ├── _get_store(...)
    │       │   └── _normalize_path_config(...)
    │       │       └── PathConfig(...)
    │       ├── _normalize_table_name(...)
    │       ├── _resolve_lakehouse_table_path(...)
    │       │   ├── _normalize_table_name(...)
    │       │   └── _resolve_lakehouse_schema(...)
    │       │       └── _normalize_schema_name(...)
    │       └── resolve_fabric_context(...)
    │           └── get_default_fabric_context(...)
    ├── build_enrichment_rule_records(...)
    │   ├── _approved_column_identity(...)
    │   │   ├── _build_metadata_column_key(...)
    │   │   │   └── _stable_metadata_key(...)
    │   │   ├── _build_metadata_table_key(...)
    │   │   │   └── _stable_metadata_key(...)
    │   │   └── _value(...)
    │   ├── _approved_review_context(...)
    │   │   ├── _build_runtime_audit_fields(...)
    │   │   │   ├── _context_get(...)
    │   │   │   ├── _current_audit_timestamp(...)
    │   │   │   │   └── _get_audit_timezone(...)
    │   │   │   │       └── _validate_audit_timezone(...)
    │   │   │   ├── _get_store(...)
    │   │   │   │   └── _normalize_path_config(...)
    │   │   │   │       └── PathConfig(...)
    │   │   │   ├── _runtime_context(...)
    │   │   │   │   └── _context_get(...)
    │   │   │   └── _safe_str(...)
    │   │   ├── _now_utc_iso(...)
    │   │   │   └── _current_audit_timestamp(...)
    │   │   │       └── _get_audit_timezone(...)
    │   │   │           └── _validate_audit_timezone(...)
    │   │   ├── _resolve_action_by(...)
    │   │   │   ├── _context_get(...)
    │   │   │   └── _runtime_context(...)
    │   │   │       └── _context_get(...)
    │   │   └── _value(...)
    │   ├── _build_dq_rule_key(...)
    │   │   └── _stable_metadata_key(...)
    │   ├── _enrichment_payload_from_review(...)
    │   ├── _json(...)
    │   └── guardrail_authoring_status(...)
    │       ├── _authoring_lifecycle(...)
    │       │   ├── _is_no_approval_required(...)
    │       │   ├── _lifecycle_fields(...)
    │       │   ├── _now_utc_iso(...)
    │       │   │   └── _current_audit_timestamp(...)
    │       │   │       └── _get_audit_timezone(...)
    │       │   │           └── …
    │       │   └── _resolve_action_by(...)
    │       │       ├── _context_get(...)
    │       │       └── _runtime_context(...)
    │       │           └── _context_get(...)
    │       └── _is_no_approval_required(...)
    └── resolve_fabric_context(...)
        └── get_default_fabric_context(...)
    ```

??? info "Internal helpers used: 10"

    This callable uses 10 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L436-L443"><code>_enrichment_options</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L629-L639"><code>_write_table_metadata_enrichment_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L599-L639"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L446-L464"><code>_render_enrichment_extra_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/config.py#L642-L681"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L467-L469"><code>_collect_enrichment_extra_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L472-L484"><code>_selected_catalogue_rows_for_enrichment</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_enrich_table_metadata`
- Short name: `widget_enrich_table_metadata`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `642`
- Inbound references count: 0
- Outbound references count: 8
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: evidence, metadata lakehouse, guardrails

### Implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Guardrail governance review`.
- **inputs:** See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.
- **output:** Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- `fabricops_kit.governance_review._collect_enrichment_extra_fields`
- `fabricops_kit.governance_review._enrichment_options`
- `fabricops_kit.governance_review._render_enrichment_extra_fields`
- `fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.governance_review._write_table_metadata_enrichment_records`
- `fabricops_kit.governance_review.build_enrichment_rule_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L642-L776">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/ad0e01454e054556946f1727b681a5d0bef553b2/src/fabricops_kit/governance_review.py#L642-L776</a>
- Start line: `642`
- End line: `776`
- Signature:

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    spark_session: Any,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="widget_select_guardrail_target/"><code>fabricops_kit.governance_review.widget_select_guardrail_target</code></a>
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>
- <details class="glossary-chip"><summary>Metadata lakehouse</summary>Configured Fabric Lakehouse target where FabricOps stores metadata tables.</details>
- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
