# write_warehouse_table

Write a DataFrame to a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/fabric_input_output.py:501`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/fabric_input_output.py#L501-L566">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use for target writes after guardrails pass and the configured output layer is a warehouse table.

**Do not use when:**

- Do not use for lakehouse table writes, lakehouse Files writes, or metadata evidence writes.

**Additional context:**

Writes a DataFrame to a configured Fabric Warehouse destination for pipeline outputs that belong in warehouse storage.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_warehouse_table(serving_df, CONFIG, env="Sandbox", target="Warehouse", schema="dbo", table="orders_serving", mode="append")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `config` | `FrameworkConfig \| dict` | Yes | FabricOps FrameworkConfig or compatible config object. |
| `env` | `str` | Yes | Environment name in the config mapping, for example `"Sandbox"` or `"DE"`. |
| `target` | `str` | Yes | Warehouse target name under the selected environment, for example `"Warehouse"` or `"wh_Bronze"`. |
| `schema` | `str` | Yes | Warehouse schema name, for example `"dbo"`. |
| `table` | `str` | Yes | Warehouse table name. |
| `mode` | `str, default "append"` | No | Spark write mode, for example `"append"` or `"overwrite"`. |

## Returns

None; the DataFrame is written to the configured warehouse table.

### Return interpretation

A successful write means the helper submitted the DataFrame write to the configured warehouse target; verify downstream table state for business checks.

## Raises / Errors

Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.

### Common failure causes

- The warehouse target is missing from configuration.
- The target table name or write mode is invalid.
- Warehouse connector support is unavailable.
- The caller lacks write permission.

## Relationships

### Used by

Not documented yet

### Calls

Not documented yet

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `00_env_config`
- `02_pipeline`

**Side effects:**

Writes data to a Fabric warehouse table using the selected mode.

**Notes:**

Side effect: performs a write operation to the target warehouse object via
Fabric runtime connector APIs.

</details>

??? info "Call flow"

    ```text
    write_warehouse_table(...)
    └── _get_store(...)
        └── _normalize_path_config(...)
            └── PathConfig(...)
    ```

??? info "Internal helpers used: 2"

    This callable uses 2 internal helpers for rule parsing and fabric or spark access.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L651-L691"><code>_normalize_path_config</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L694-L733"><code>_get_store</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.fabric_input_output.write_warehouse_table`
- Short name: `write_warehouse_table`
- Module: `fabric_input_output`
- Classification: Callable
- Related module: `fabric_input_output`
- Source file path: `src/fabricops_kit/fabric_input_output.py`
- Source line: `501`
- Inbound references count: 0
- Outbound references count: 0
- Used in templates: 00_env_config, 02_pipeline
- Glossary terms: target table, guardrail

### AI implementation contract

- **required_context:** Requires the FrameworkConfig or compatible CONFIG from 00_env_config plus the intended env name; never hardcode Fabric workspace or item identifiers.
- **inputs:** df, config, env, target, schema, table, and write mode.
- **output:** None; the DataFrame is written to the configured warehouse table.
- **side_effects:** Writes data to a Fabric warehouse table using the selected mode.
- **failure_modes:** Raises configuration, Spark connector, or warehouse write errors when the target/table cannot be written.
- **verification:** Verify guardrails passed, confirm schema/table routing from CONFIG, and check the intended write mode before calling.

### Inbound references

Not documented yet

### Outbound references

Not documented yet

### Raw source metadata

- Source file path: `src/fabricops_kit/fabric_input_output.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/fabric_input_output.py#L501-L566">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/fabric_input_output.py#L501-L566</a>
- Start line: `501`
- End line: `566`
- Signature:

```python
def write_warehouse_table(df, config, env, target, schema, table, mode='append')
```

### Internal relationship graph

### Public related functions

- <a href="../read_warehouse_table/"><code>fabricops_kit.fabric_input_output.read_warehouse_table</code></a>
- <a href="../write_lakehouse_table/"><code>fabricops_kit.fabric_input_output.write_lakehouse_table</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 2
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Target table:** An output table written by the pipeline.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
