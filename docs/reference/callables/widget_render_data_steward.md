# widget_render_data_steward

Render the standalone data-steward intake widget.

## Use this when

Render the standalone data-steward intake widget.

## Do not use this for

Not documented yet

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
      <th>What it means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Configuration containing steward widget fields and metadata routing.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Environment key configured by ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="What it means">Fabric Spark session used for metadata reads and append-only writes.</td>
    </tr>
  </tbody>
</table>
</div>

<details class="reference-signature-details">
<summary>Full signature</summary>

```python
def widget_render_data_steward(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

</details>

## Output

dict[str, Any]
    Rendered widget controls keyed for notebook customization.

## Raises

Not documented yet

## Side effects

Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

</details>

<details class="reference-metadata-details">
<summary>AI implementation contract</summary>

These fields are generated for agents and maintainers, not for quick-start reading.

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing steward widget fields and metadata routing.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads and append-only writes.
- **output:** dict[str, Any]
    Rendered widget controls keyed for notebook customization.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

</details>

<details class="reference-metadata-details">
<summary>Function manifest</summary>

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_data_steward`
- Short name: `widget_render_data_steward`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1498`
- Inbound references count: 0
- Outbound references count: 1

</details>

<details class="reference-metadata-details">
<summary>Raw inbound and outbound references</summary>

### Inbound references

Not documented yet

### Outbound references

- <a href="../internal/data_agreement__render_maintenance_widget/"><code>fabricops_kit.data_agreement._render_maintenance_widget</code></a>

</details>

## Source code

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/5b6a5693130e525f919566c2115ac67da9c6faef/src/fabricops_kit/data_agreement.py#L1498-L1515">View widget_render_data_steward on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_render_data_steward(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render append-only data steward create/update maintenance.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing steward widget fields and metadata routing.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.

    Returns
    -------
    dict[str, Any]
        Rendered widget controls keyed for notebook customization.
    """
    return _render_maintenance_widget(spark=spark, config=config, env_name=env_name, kind="data_steward_widget")
```

</details>
