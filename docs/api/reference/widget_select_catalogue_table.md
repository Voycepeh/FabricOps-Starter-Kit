# widget_select_catalogue_table

Render a searchable selector for latest successful catalogue profiles.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:300`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L300-L341">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use at the start of 03_governance before column context, DQ, or classification review widgets need a selected table.

**Additional context:**

Renders a selector for catalogue profile rows so governance reviewers can choose the table they are reviewing.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
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

ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.

### Return interpretation

The widget stores the selected table in notebook state; call get_selected_catalogue_table after the user chooses a row.

## Raises / Errors

Not documented yet

### Common failure causes

- No catalogue profile rows are available.
- The user has not selected a table.
- Profile metadata cannot be read.
- Widget state was reset by rerunning cells.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_table_options`
- `fabricops_kit.governance_review._coerce_rows`

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
    widget_select_catalogue_table(...)
    ├── _catalogue_table_options(...)
    │   ├── _build_metadata_table_key(...)
    │   │   └── _stable_metadata_key(...)
    │   ├── _is_success(...)
    │   │   └── _value(...)
    │   └── _value(...)
    ├── _coerce_rows(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   └── _normalize_schema_name(...)
    └── read_lakehouse_table(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_table_path(...)
            ├── _normalize_table_name(...)
            └── _resolve_lakehouse_schema(...)
                └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 9"

    This callable uses 9 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L77-L78"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L221-L270"><code>_catalogue_table_options</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/fabric_input_output.py#L152-L157"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/metadata.py#L72-L74"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/fabric_input_output.py#L105-L116"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/config.py#L627-L667"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L74-L75"><code>_is_success</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L70-L71"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_select_catalogue_table`
- Short name: `widget_select_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `300`
- Inbound references count: 0
- Outbound references count: 4
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, notebook template

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** config : FrameworkConfig or dict
    Runtime config containing the metadata lakehouse route.
env : str
    Environment used to read ``METADATA_DATA_CATALOGUE``.
spark_session : pyspark.sql.SparkSession
    Spark session used for the catalogue read.
- **output:** ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_table_options`
- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L300-L341">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c532a3833c706478ccf9b4b479d2157a0e5f129c/src/fabricops_kit/governance_review.py#L300-L341</a>
- Start line: `300`
- End line: `341`
- Signature:

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 9
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
