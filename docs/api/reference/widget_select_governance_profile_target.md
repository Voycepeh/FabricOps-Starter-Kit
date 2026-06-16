# widget_select_governance_profile_target

Render dependent selectors for physical catalogue profile targets.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:359`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L359-L442">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance when a reviewer needs to select a governed physical table by asset/lakehouse, schema/layer, and table name before choosing the profile date/run to review.

**Do not use when:**

- Do not use for non-interactive pipeline execution, when code already has a specific profile_run_id, or when the flat latest-profile table selector is sufficient. Do not use it to decide pipeline ownership; source/target profile stage and pipeline metadata are supporting evidence only.

**Additional context:**

Renders dependent profile-target selectors so governance reviewers choose the physical table first, then select the profile date/run to review. Source/target profile stage and pipeline metadata remain visible as supporting evidence but are not part of table identity.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_governance_profile_target(
    config: Any,
    env: str,
    spark_session: Any,
):
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | Yes | Runtime config containing the metadata lakehouse route. |
| `env` | `str` | Yes | Environment used to read ``METADATA_DATA_CATALOGUE``. |
| `spark_session` | `Any` | Yes | Spark session used for the catalogue read. |

## Returns

ipywidgets.VBox
    Container with dependent asset, schema/layer, table, and profile-run
    dropdowns. The selected profile row identity is available through
    ``get_selected_catalogue_table``.

### Return interpretation

The widget stores the selected physical table and profile run in notebook state; call get_selected_catalogue_table after the reviewer chooses a profile target.

## Raises / Errors

Not documented yet

### Common failure causes

- METADATA_DATA_CATALOGUE has no rows because 02_pipeline profiling has not run.
- Catalogue rows are missing stable physical identity fields such as asset/lakehouse, schema/layer, or table name.
- ipywidgets is unavailable in the notebook runtime.
- No profiled_at or profile run metadata exists, causing profile labels to be less useful.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_profile_target_model`
- `fabricops_kit.governance_review._coerce_rows`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `03_governance`

**Side effects:**

Not documented yet

**Notes:**

Table identity is based on physical catalogue fields and intentionally
excludes ``profile_stage`` and pipeline metadata. Source/target stage and
pipeline values remain visible as profile evidence for the selected table.

</details>

??? info "Call flow"

    ```text
    widget_select_governance_profile_target(...)
    ├── _catalogue_profile_target_model(...)
    │   ├── _catalogue_physical_identity(...)
    │   │   ├── _build_metadata_table_key(...)
    │   │   │   └── _stable_metadata_key(...)
    │   │   ├── _first_present(...)
    │   │   │   └── _value(...)
    │   │   └── _value(...)
    │   ├── _is_success(...)
    │   │   └── _value(...)
    │   └── _value(...)
    ├── _coerce_rows(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _normalize_schema_name(...)
    └── read_lakehouse_table(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        │   └── _normalize_path_config(...)
        │       └── PathConfig(...)
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_table_path(...)
            ├── _normalize_table_name(...)
            └── _resolve_lakehouse_schema(...)
                └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 12"

    This callable uses 12 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L250-L270"><code>_catalogue_physical_identity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L231-L237"><code>_first_present</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L273-L328"><code>_catalogue_profile_target_model</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L65-L70"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L77-L78"><code>_is_success</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L73-L74"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_select_governance_profile_target`
- Short name: `widget_select_governance_profile_target`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `359`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, source table, target table, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** config : FrameworkConfig or dict
    Runtime config containing the metadata lakehouse route.
env : str
    Environment used to read ``METADATA_DATA_CATALOGUE``.
spark_session : pyspark.sql.SparkSession
    Spark session used for the catalogue read.
- **output:** ipywidgets.VBox
    Container with dependent asset, schema/layer, table, and profile-run
    dropdowns. The selected profile row identity is available through
    ``get_selected_catalogue_table``.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_profile_target_model`
- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L359-L442">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e8645ff20c03192521dcf46b2587df5fb13d8754/src/fabricops_kit/governance_review.py#L359-L442</a>
- Start line: `359`
- End line: `442`
- Signature:

```python
def widget_select_governance_profile_target(
    config: Any,
    env: str,
    spark_session: Any,
):
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 12
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
