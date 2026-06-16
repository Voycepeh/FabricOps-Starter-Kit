# widget_select_guardrail_target

Render an interactive target selector for guardrail authoring and governance review.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:1863`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L1863-L1942">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use at the start of 02_pipeline authoring or 03_governance review when a user must choose which profiled table to work on.

**Do not use when:**

- Do not use for automatic pipeline enforcement or to write metadata; this selector reads metadata and prepares widget state only.

**Additional context:**

Renders an interactive selector that reads catalogue profile evidence, existing guardrail rules, and table governance policy to create the handover state for guardrail authoring or review.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_guardrail_target(
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
| `config` | `Any` | Yes | Runtime configuration containing metadata lakehouse routing. |
| `env` | `str` | Yes | Environment name used to read metadata tables. |
| `spark_session` | `Any` | Yes | Spark session for metadata reads. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The returned state includes environment, dataset, table, metadata keys, profile rows, existing rules, and governance policy values for downstream widgets.

## Raises / Errors

Not documented yet

### Common failure causes

- METADATA_DATA_CATALOGUE has no profile evidence.
- The selected table lacks metadata identity fields.
- Metadata tables cannot be read.
- ipywidgets is unavailable.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.governance_review._filter_table_rows`
- `fabricops_kit.governance_review._read_metadata_table_or_empty`
- `fabricops_kit.governance_review.resolve_table_governance_policy`
- `fabricops_kit.metadata._build_metadata_table_key`

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
    widget_select_guardrail_target(...)
    ├── _build_metadata_table_key(...)
    │   └── _stable_metadata_key(...)
    ├── _filter_table_rows(...)
    ├── _read_metadata_table_or_empty(...)
    │   ├── _coerce_rows(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   └── _normalize_schema_name(...)
    │   ├── _is_table_not_found_error(...)
    │   └── read_lakehouse_table(...)
    │       ├── _get_spark(...)
    │       ├── _get_store(...)
    │       │   └── _normalize_path_config(...)
    │       │       └── PathConfig(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_table_path(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_schema(...)
    │               └── _normalize_schema_name(...)
    └── resolve_table_governance_policy(...)
        └── _coerce_rows(...)
    ```

??? info "Internal helpers used: 10"

    This callable uses 10 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L1793-L1807"><code>_filter_table_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L206-L226"><code>_is_table_not_found_error</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L1775-L1790"><code>_read_metadata_table_or_empty</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/config.py#L661-L701"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/config.py#L704-L743"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L65-L70"><code>_coerce_rows</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_select_guardrail_target`
- Short name: `widget_select_guardrail_target`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `1863`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 02_pipeline, 03_governance
- Glossary terms: catalogue evidence, guardrail, metadata lakehouse, notebook template

### AI implementation contract

- **required_context:** Starter template: `02_pipeline / 03_governance`; segment: `Guardrail authoring`.
- **inputs:** See the source docstring for the notebook runtime, Spark session, state, and record parameters accepted by this helper.
- **output:** Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.governance_review._filter_table_rows`
- `fabricops_kit.governance_review._read_metadata_table_or_empty`
- `fabricops_kit.governance_review.resolve_table_governance_policy`
- `fabricops_kit.metadata._build_metadata_table_key`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L1863-L1942">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3e1e2017ffc6e6594c131b4f0adb305e6966a58/src/fabricops_kit/governance_review.py#L1863-L1942</a>
- Start line: `1863`
- End line: `1942`
- Signature:

```python
def widget_select_guardrail_target(
    config: Any,
    env: str,
    spark_session: Any,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 10
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

No related guides documented.
