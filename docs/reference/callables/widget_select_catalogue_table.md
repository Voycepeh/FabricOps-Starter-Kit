# widget_select_catalogue_table

Render a searchable selector for latest successful catalogue profiles.

## What this is for and when to use it

Render a searchable selector for latest successful catalogue profiles.

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

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

### Call flow

```text
widget_select_catalogue_table(...)
├── _catalogue_table_options(...)
│   ├── _build_metadata_table_key(...)
│   │   └── _stable_metadata_key(...)
│   ├── _is_success(...)
│   │   └── _value(...)
│   └── _value(...)
├── _coerce_rows(...)
└── read_lakehouse_table(...)
    ├── _current_database_matches(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    ├── _normalize_table_name(...)
    ├── _registered_table_identifier(...)
    │   ├── _normalize_table_name(...)
    │   └── _quote_identifier(...)
    └── _uses_registered_metadata_table(...)
```

### Internal helpers used by this callable

### `def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]`

**What it does:**

Return one option per logical table using its latest successful profile.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L258-L307">View `_catalogue_table_options` on GitHub</a>

**Code:**

```python
def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one option per logical table using its latest successful profile.

    Parameters
    ----------
    catalogue_rows : iterable of dict
        Rows from ``METADATA_DATA_CATALOGUE``.

    Returns
    -------
    list[dict[str, Any]]
        Stable table selections sorted by display label.

    Raises
    ------
    ValueError
        If there are no catalogue rows or no successful profile rows.
    """
    rows = [dict(r) for r in catalogue_rows or []]
    if not rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 02_pipeline profiling before 03_governance.")
    successes = [r for r in rows if _is_success(r)]
    if not successes:
        raise ValueError("METADATA_DATA_CATALOGUE has no successful profile evidence for governance review.")
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in successes:
        env = str(_value(row, "environment_name"))
        dataset = str(_value(row, "dataset_name"))
        table = str(_value(row, "table_name"))
        key = (env, dataset, table)
        current = latest.get(key)
        sort_key = (str(_value(row, "profiled_at")), str(_value(row, "profile_run_id")), str(_value(row, "profile_stage")))
        if current is None or sort_key > current["_sort_key"]:
            latest[key] = {"row": row, "_sort_key": sort_key}
    options = []
    for (env, dataset, table), item in latest.items():
        row = item["row"]
        table_key = str(_value(row, "metadata_table_key") or _build_metadata_table_key(env, dataset, table))
        profile_run_id = str(_value(row, "profile_run_id"))
        profile_stage = str(_value(row, "profile_stage"))
        layer = str(_value(row, "layer"))
        asset_kind = str(_value(row, "asset_kind"))
        label = f"{env} / {dataset} / {layer or '-'} / {asset_kind or '-'} / {table} / {profile_stage or '-'} / {profile_run_id}"
        options.append({
            "label": label,
            "value": json.dumps({"environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key, "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at"))}, sort_keys=True),
            "environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key,
            "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at")),
        })
    return sorted(options, key=lambda r: r["label"])
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_catalogue_table_options`.

### `def _is_success(row: dict[str, Any]) -> bool`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L74-L75">View `_is_success` on GitHub</a>

**Code:**

```python
def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_is_success`.

### `def _value(row: dict[str, Any], name: str, default: Any='') -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L70-L71">View `_value` on GitHub</a>

**Code:**

```python
def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_value`.

### `def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L149-L150">View `_build_metadata_table_key` on GitHub</a>

**Code:**

```python
def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name)
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_build_metadata_table_key`.

### `def _stable_metadata_key(*parts: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L144-L146">View `_stable_metadata_key` on GitHub</a>

**Code:**

```python
def _stable_metadata_key(*parts: Any) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_stable_metadata_key`.

### `def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L62-L67">View `_coerce_rows` on GitHub</a>

**Code:**

```python
def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_coerce_rows`.


</details>

## Source

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L337-L378">View widget_select_catalogue_table on GitHub</a>

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
- Source line: `337`
- Inbound references count: 0
- Outbound references count: 3

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

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_table_options`
- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L337-L378">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L337-L378</a>
- Start line: `337`
- End line: `378`
- Signature:

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
```

### Internal relationship graph

### Public related functions

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation helpers

### Call flow

```text
widget_select_catalogue_table(...)
├── _catalogue_table_options(...)
│   ├── _build_metadata_table_key(...)
│   │   └── _stable_metadata_key(...)
│   ├── _is_success(...)
│   │   └── _value(...)
│   └── _value(...)
├── _coerce_rows(...)
└── read_lakehouse_table(...)
    ├── _current_database_matches(...)
    ├── _get_spark(...)
    ├── _get_store(...)
    ├── _normalize_table_name(...)
    ├── _registered_table_identifier(...)
    │   ├── _normalize_table_name(...)
    │   └── _quote_identifier(...)
    └── _uses_registered_metadata_table(...)
```

### Internal helpers used by this callable

### `def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]`

**What it does:**

Return one option per logical table using its latest successful profile.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L258-L307">View `_catalogue_table_options` on GitHub</a>

**Code:**

```python
def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one option per logical table using its latest successful profile.

    Parameters
    ----------
    catalogue_rows : iterable of dict
        Rows from ``METADATA_DATA_CATALOGUE``.

    Returns
    -------
    list[dict[str, Any]]
        Stable table selections sorted by display label.

    Raises
    ------
    ValueError
        If there are no catalogue rows or no successful profile rows.
    """
    rows = [dict(r) for r in catalogue_rows or []]
    if not rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 02_pipeline profiling before 03_governance.")
    successes = [r for r in rows if _is_success(r)]
    if not successes:
        raise ValueError("METADATA_DATA_CATALOGUE has no successful profile evidence for governance review.")
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in successes:
        env = str(_value(row, "environment_name"))
        dataset = str(_value(row, "dataset_name"))
        table = str(_value(row, "table_name"))
        key = (env, dataset, table)
        current = latest.get(key)
        sort_key = (str(_value(row, "profiled_at")), str(_value(row, "profile_run_id")), str(_value(row, "profile_stage")))
        if current is None or sort_key > current["_sort_key"]:
            latest[key] = {"row": row, "_sort_key": sort_key}
    options = []
    for (env, dataset, table), item in latest.items():
        row = item["row"]
        table_key = str(_value(row, "metadata_table_key") or _build_metadata_table_key(env, dataset, table))
        profile_run_id = str(_value(row, "profile_run_id"))
        profile_stage = str(_value(row, "profile_stage"))
        layer = str(_value(row, "layer"))
        asset_kind = str(_value(row, "asset_kind"))
        label = f"{env} / {dataset} / {layer or '-'} / {asset_kind or '-'} / {table} / {profile_stage or '-'} / {profile_run_id}"
        options.append({
            "label": label,
            "value": json.dumps({"environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key, "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at"))}, sort_keys=True),
            "environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key,
            "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at")),
        })
    return sorted(options, key=lambda r: r["label"])
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_catalogue_table_options`.

### `def _is_success(row: dict[str, Any]) -> bool`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L74-L75">View `_is_success` on GitHub</a>

**Code:**

```python
def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_is_success`.

### `def _value(row: dict[str, Any], name: str, default: Any='') -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L70-L71">View `_value` on GitHub</a>

**Code:**

```python
def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_value`.

### `def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L149-L150">View `_build_metadata_table_key` on GitHub</a>

**Code:**

```python
def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
    return _stable_metadata_key(environment_name, dataset_name, table_name)
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_build_metadata_table_key`.

### `def _stable_metadata_key(*parts: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/metadata.py#L144-L146">View `_stable_metadata_key` on GitHub</a>

**Code:**

```python
def _stable_metadata_key(*parts: Any) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_stable_metadata_key`.

### `def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/governance_review.py#L62-L67">View `_coerce_rows` on GitHub</a>

**Code:**

```python
def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
```

**Used here because:**

`widget_select_catalogue_table` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_select_catalogue_table` or another caller that reaches `_coerce_rows`.


</details>
