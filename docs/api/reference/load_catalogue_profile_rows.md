# load_catalogue_profile_rows

Load column profile rows for the selected catalogue table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/governance_review.py:440`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L440-L456">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 03_governance after selecting a catalogue table and before rendering review widgets.

**Additional context:**

Loads catalogue profile evidence rows for a selected table so governance review widgets can display approved or proposed context.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def load_catalogue_profile_rows(
    config: Any,
    env: str,
    selection: dict[str, Any],
    spark_session: Any,
) -> list[dict[str, Any]]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `Any` | Yes | Not documented yet |
| `env` | `str` | Yes | Not documented yet |
| `selection` | `dict[str, Any]` | Yes | Not documented yet |
| `spark_session` | `Any` | Yes | Not documented yet |

## Returns

Not documented yet

### Return interpretation

Returned rows provide the profile context that review widgets display. Empty results usually mean evidence has not been recorded for that table or stage.

## Raises / Errors

Not documented yet

### Common failure causes

- The selected table context is incomplete.
- The metadata lakehouse cannot be read.
- Profile evidence has not been generated yet.
- Filters for dataset, table, or stage do not match stored evidence.

## Relationships

### Used by

- `fabricops_kit.governance_review._review_governance_evidence`

### Calls

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_physical_identity`
- `fabricops_kit.governance_review._coerce_rows`
- `fabricops_kit.governance_review._is_success`
- `fabricops_kit.governance_review._value`

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
    load_catalogue_profile_rows(...)
    ├── _catalogue_physical_identity(...)
    │   ├── _build_metadata_table_key(...)
    │   │   └── _stable_metadata_key(...)
    │   ├── _first_present(...)
    │   │   └── _value(...)
    │   └── _value(...)
    ├── _coerce_rows(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── _normalize_path_config(...)
    │   │       └── PathConfig(...)
    │   └── _normalize_schema_name(...)
    ├── _is_success(...)
    │   └── _value(...)
    ├── _value(...)
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

??? info "Internal helpers used: 11"

    This callable uses 11 internal helpers for metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L245-L265"><code>_catalogue_physical_identity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L226-L232"><code>_first_present</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L65-L70"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L77-L78"><code>_is_success</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L73-L74"><code>_value</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.load_catalogue_profile_rows`
- Short name: `load_catalogue_profile_rows`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `440`
- Inbound references count: 1
- Outbound references count: 6
- Used in templates: 03_governance
- Glossary terms: catalogue evidence, accepted catalogue profile evidence, metadata lakehouse

### AI implementation contract

- **required_context:** Starter template: `03_governance`; segment: `Governance review`.
- **inputs:** Not documented yet
- **output:** Not documented yet
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

- `fabricops_kit.governance_review._review_governance_evidence`

### Outbound references

- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_physical_identity`
- `fabricops_kit.governance_review._coerce_rows`
- `fabricops_kit.governance_review._is_success`
- `fabricops_kit.governance_review._value`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L440-L456">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/e4698def2c6568d6397a09f8202239faa01c2549/src/fabricops_kit/governance_review.py#L440-L456</a>
- Start line: `440`
- End line: `456`
- Signature:

```python
def load_catalogue_profile_rows(
    config: Any,
    env: str,
    selection: dict[str, Any],
    spark_session: Any,
) -> list[dict[str, Any]]:
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 11
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Accepted catalogue profile evidence:** The approved profile record that FabricOps treats as the trusted baseline for a table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Governance Review](../../how-fabricops-works/governance-review.md)
- [Metadata Tables](../../how-fabricops-works/metadata-tables.md)
