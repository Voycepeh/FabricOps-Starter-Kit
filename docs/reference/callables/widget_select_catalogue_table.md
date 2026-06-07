# widget_select_catalogue_table

Render a searchable selector for latest successful catalogue profiles.

## What this is for

Render a searchable selector for latest successful catalogue profiles.

## When to use it

- Render a searchable selector for latest successful catalogue profiles.

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
      <td data-label="Meaning">Runtime config containing the metadata lakehouse route.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment used to read ``METADATA_DATA_CATALOGUE``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark session used for the catalogue read.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.

## Raises

Not documented yet

## Side effects

Not documented yet

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/governance_review.py#L288-L329">View widget_select_catalogue_table on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any):
    """Render a searchable selector for latest successful catalogue tables.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Runtime config containing the metadata lakehouse route.
    env : str
        Environment used to read ``METADATA_DATA_CATALOGUE``.
    spark_session : pyspark.sql.SparkSession
        Spark session used for the catalogue read.

    Returns
    -------
    ipywidgets.Combobox
        Searchable selector whose value stores stable JSON identity.
    """
    global _SELECTED_CATALOGUE_TABLE
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    options = _catalogue_table_options(rows)
    by_label = {o["label"]: o for o in options}
    combo = widgets.Combobox(placeholder="Search profiled tables", options=[o["label"] for o in options], description="Table", ensure_option=True, layout=widgets.Layout(width="980px"))
    context = widgets.HTML()

    def select(label: str) -> None:
        global _SELECTED_CATALOGUE_TABLE
        option = by_label.get(label) or options[0]
        _SELECTED_CATALOGUE_TABLE = {k: option[k] for k in ["environment_name", "dataset_name", "table_name", "metadata_table_key", "profile_run_id", "profile_stage", "layer", "asset_kind", "profiled_at"]}
        context.value = f"<b>Selected table:</b> {_SELECTED_CATALOGUE_TABLE['environment_name']} / {_SELECTED_CATALOGUE_TABLE['dataset_name']} / {_SELECTED_CATALOGUE_TABLE['table_name']}<br/><b>Profile run:</b> {_SELECTED_CATALOGUE_TABLE['profile_run_id']} ({_SELECTED_CATALOGUE_TABLE['profile_stage']})"

    def on_change(change: dict[str, Any]) -> None:
        if change.get("name") == "value" and change.get("new") in by_label:
            select(change["new"])

    combo.observe(on_change, names="value")
    combo.value = options[0]["label"]
    select(combo.value)
    ip.display(widgets.VBox([combo, context]))
    return combo
```

</details>

## AI / machine-readable metadata

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.governance_review.widget_select_catalogue_table`
- Short name: `widget_select_catalogue_table`
- Module: `governance_review`
- Classification: Callable
- Related module: `governance_review`
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `288`
- Inbound references count: 0
- Outbound references count: 3

### AI implementation contract

- **required_context:** Starter template: `03_review`; segment: `Governance review`.
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

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/governance_review.py#L288-L329">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4c16c62a2fd27c5a88a51c78e285c4b6e922580a/src/fabricops_kit/governance_review.py#L288-L329</a>
- Start line: `288`
- End line: `329`
- Signature:

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

- <a href="../internal/governance_review__catalogue_table_options/"><code>fabricops_kit.governance_review._catalogue_table_options</code></a>
- <a href="../internal/governance_review__coerce_rows/"><code>fabricops_kit.governance_review._coerce_rows</code></a>

</details>
