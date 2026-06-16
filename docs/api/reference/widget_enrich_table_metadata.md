# widget_enrich_table_metadata

Render a consolidated column metadata enrichment widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:600`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L600-L712">View on GitHub</a>
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

Widget state containing editable row controls, record builders, and a save callback for column context and classification metadata.

### Return interpretation

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_COLUMN_CONTEXT and METADATA_COLUMN_CLASSIFICATION.

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

- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._collect_enrichment_extra_fields`
- `fabricops_kit.governance_review._enrichment_options`
- `fabricops_kit.governance_review._render_enrichment_extra_fields`
- `fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.governance_review._write_table_metadata_enrichment_records`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

This widget enriches descriptive governance metadata for profiled catalogue
columns. It does not write DQ rules, guardrail results, or catalogue profile
evidence; runtime DQ remains part of guardrail authoring and review. Custom
enrichment fields are stored as ``custom_fields_json`` to match the
schema-safe ``01_agreement`` custom-field pattern without creating dynamic
physical metadata columns.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    widget_enrich_table_metadata(...)
    ├── _build_classification_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _build_column_context_records(...)
    │   ├── _approved_column_identity(...)
    │   │   └── …
    │   ├── _approved_review_context(...)
    │   │   └── …
    │   └── _json(...)
    ├── _collect_enrichment_extra_fields(...)
    ├── _enrichment_options(...)
    ├── _render_enrichment_extra_fields(...)
    ├── _selected_catalogue_rows_for_enrichment(...)
    │   └── _value(...)
    ├── _value(...)
    └── _write_table_metadata_enrichment_records(...)
        ├── _configured_lakehouse_schema(...)
        │   └── …
        └── write_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 27"

    This callable uses 27 internal helpers for audit timestamp, metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L66-L72"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L58-L63"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L84-L85"><code>_build_metadata_column_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L518-L525"><code>_enrichment_options</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L569-L597"><code>_write_table_metadata_enrichment_records</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L471-L476"><code>_json</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L653-L693"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L528-L546"><code>_render_enrichment_extra_fields</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L696-L735"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L97-L109"><code>_approved_column_identity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L91-L94"><code>_approved_review_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L448-L469"><code>_build_classification_records</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L344-L358"><code>_build_column_context_records</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L549-L551"><code>_collect_enrichment_extra_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L68-L72"><code>_resolve_action_by</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L554-L566"><code>_selected_catalogue_rows_for_enrichment</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L73-L74"><code>_value</code></a>
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
- Source line: `600`
- Inbound references count: 0
- Outbound references count: 8
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, metadata lakehouse, guardrail

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Guardrail governance review`.
- **inputs:** See the source docstring for the selected guardrail state, configuration, environment, and Spark session parameters.
- **output:** Widget state containing editable row controls, record builders, and a save callback for column context and classification metadata.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._build_classification_records`
- `fabricops_kit.governance_review._build_column_context_records`
- `fabricops_kit.governance_review._collect_enrichment_extra_fields`
- `fabricops_kit.governance_review._enrichment_options`
- `fabricops_kit.governance_review._render_enrichment_extra_fields`
- `fabricops_kit.governance_review._selected_catalogue_rows_for_enrichment`
- `fabricops_kit.governance_review._value`
- `fabricops_kit.governance_review._write_table_metadata_enrichment_records`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L600-L712">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/governance_review.py#L600-L712</a>
- Start line: `600`
- End line: `712`
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

- Internal helper count: 27
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
