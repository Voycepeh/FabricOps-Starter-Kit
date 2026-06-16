# widget_enrich_table_metadata

Render a consolidated column metadata enrichment widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:619`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L619-L724">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.

**Do not use when:**

- Do not use to author DQ rules or runtime enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.

**Additional context:**

Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profile evidence.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    config: Any,
    env: str,
    spark_session: Any,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `guardrail_state` | `Mapping[str, Any]` | Yes | Target handover state returned by :func:`widget_select_guardrail_target`. |
| `config` | `Any` | Yes | Runtime configuration from ``00_env_config`` containing metadata routing and enrichment dropdown/custom-field settings. |
| `env` | `str` | Yes | Environment key used to route metadata writes to the configured ``metadata`` target. |
| `spark_session` | `Any` | Yes | Spark session used to create write DataFrames. |

## Returns

Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.

### Return interpretation

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- The selected guardrail target has no column-level catalogue evidence.
- Configured custom fields omit a field name.
- Metadata lakehouse writes cannot be routed through 00_env_config.

## Relationships

### Used by

Not documented yet

### Calls

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
    │       └── _resolve_lakehouse_table_path(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_schema(...)
    │               └── _normalize_schema_name(...)
    └── build_enrichment_rule_records(...)
        ├── _approved_column_identity(...)
        │   ├── _build_metadata_column_key(...)
        │   │   └── _stable_metadata_key(...)
        │   ├── _build_metadata_table_key(...)
        │   │   └── _stable_metadata_key(...)
        │   └── _value(...)
        ├── _approved_review_context(...)
        │   ├── _build_runtime_audit_fields(...)
        │   │   ├── _context_get(...)
        │   │   ├── _current_audit_timestamp(...)
        │   │   │   └── _get_audit_timezone(...)
        │   │   │       └── _validate_audit_timezone(...)
        │   │   ├── _get_store(...)
        │   │   │   └── _normalize_path_config(...)
        │   │   │       └── PathConfig(...)
        │   │   ├── _runtime_context(...)
        │   │   │   └── _context_get(...)
        │   │   └── _safe_str(...)
        │   ├── _now_utc_iso(...)
        │   │   └── _current_audit_timestamp(...)
        │   │       └── _get_audit_timezone(...)
        │   │           └── _validate_audit_timezone(...)
        │   ├── _resolve_action_by(...)
        │   │   ├── _context_get(...)
        │   │   └── _runtime_context(...)
        │   │       └── _context_get(...)
        │   └── _value(...)
        ├── _build_dq_rule_key(...)
        │   └── _stable_metadata_key(...)
        ├── _enrichment_payload_from_review(...)
        ├── _json(...)
        └── guardrail_authoring_status(...)
            ├── _now_utc_iso(...)
            │   └── _current_audit_timestamp(...)
            │       └── _get_audit_timezone(...)
            │           └── _validate_audit_timezone(...)
            └── _resolve_action_by(...)
                ├── _context_get(...)
                └── _runtime_context(...)
                    └── _context_get(...)
    ```

??? info "Internal helpers used: 10"

    This callable uses 10 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L438-L445"><code>_enrichment_options</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L605-L616"><code>_write_table_metadata_enrichment_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L651-L691"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L448-L466"><code>_render_enrichment_extra_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/config.py#L694-L733"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L469-L471"><code>_collect_enrichment_extra_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L474-L486"><code>_selected_catalogue_rows_for_enrichment</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L72-L73"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_enrich_table_metadata`
- Short name: `widget_enrich_table_metadata`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `619`
- Inbound references count: 0
- Outbound references count: 7
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: catalogue evidence, metadata lakehouse, guardrail

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Guardrail governance review`.
- **inputs:** See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.
- **output:** Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._collect_enrichment_extra_fields`
- `fabricops_kit.governance_review._enrichment_options`
- `fabricops_kit.governance_review._render_enrichment_extra_fields`
- `fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.governance_review._write_table_metadata_enrichment_records`
- `fabricops_kit.governance_review.build_enrichment_rule_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L619-L724">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1464ebcaec453298d8336116e90310bdf827013d/src/fabricops_kit/governance_review.py#L619-L724</a>
- Start line: `619`
- End line: `724`
- Signature:

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    config: Any,
    env: str,
    spark_session: Any,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../widget_select_guardrail_target/"><code>fabricops_kit.governance_review.widget_select_guardrail_target</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
