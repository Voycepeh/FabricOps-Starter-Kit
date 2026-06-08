# widget_render_agreement_evidence

Render the standalone agreement-evidence widget.

## What this is for and when to use it

Render the standalone agreement-evidence widget.

- Render the standalone agreement-evidence widget.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Configuration containing agreement metadata routing and evidence table settings.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key configured by ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Fabric Spark session used for metadata reads, file writes, and append-only evidence metadata writes.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/data_agreement.py#L1462-L1495">View widget_render_agreement_evidence on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render standalone agreement evidence upload controls.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing agreement metadata routing and evidence table
        settings.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads, file writes, and
        append-only evidence metadata writes.

    Returns
    -------
    dict[str, Any]
        Rendered controls for selecting an agreement version, pasting
        metadata lakehouse evidence file paths, refreshing agreement options,
        and saving evidence metadata rows.

    Notes
    -----
    This public wrapper is intended for the separate-widget ``01_agreement`` layout.
    Evidence files must be uploaded manually to the metadata lakehouse
    ``Files`` area first. The widget appends one file-reference row per
    pasted ``Files/...`` path to ``METADATA_DATA_AGREEMENT_EVIDENCE`` and
    does not read or write binary file content.
    """
    return _render_agreement_evidence_widget(
        spark=spark,
        config=config,
        env_name=env_name,
    )
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_agreement_evidence`
- Short name: `widget_render_agreement_evidence`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1462`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing agreement metadata routing and evidence table
    settings.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads, file writes, and
    append-only evidence metadata writes.
- **output:** dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/data_agreement.py#L1462-L1495">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/d6fb0fb33beb9bd33597b485cb7d9af5e9bfe8fb/src/fabricops_kit/data_agreement.py#L1462-L1495</a>
- Start line: `1462`
- End line: `1495`
- Signature:

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation helpers

- <a href="../internal/data_agreement__render_agreement_evidence_widget/"><code>fabricops_kit.data_agreement._render_agreement_evidence_widget</code></a>

</details>
