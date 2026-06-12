# widget_select_catalogue_table

Render a searchable selector for latest successful catalogue profiles.

## Purpose

Renders a selector for catalogue profile rows so governance reviewers can choose the table they are reviewing.

## When to use this

- Use at the start of 03_governance before column context, DQ, or classification review widgets need a selected table.

## At a glance

**Do not use when:**

- Not documented yet

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Key terms

- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.
- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Related guides

- [Governance Review](../../how-fabricops-works/governance-review.md)

## Used in templates

- `03_governance`

## Used by

Not documented yet

## Calls

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_table_options`
- `fabricops_kit.governance_review._coerce_rows`

## Function details and source

### Function details

- Module: `governance_review`
- Classification: Callable
- Source file path: `src/fabricops_kit/governance_review.py`
- Source line: `300`
- Signature:

```python
def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any)
```

### Parameters

`config` : `Any`, required
: Runtime config containing the metadata lakehouse route.

`env` : `str`, required
: Environment used to read ``METADATA_DATA_CATALOGUE``.

`spark_session` : `Any`, required
: Spark session used for the catalogue read.

### Returns

ipywidgets.Combobox
    Searchable selector whose value stores stable JSON identity.

### Return interpretation

The widget stores the selected table in notebook state; call get_selected_catalogue_table after the user chooses a row.

### Common failure causes

- No catalogue profile rows are available.
- The user has not selected a table.
- Profile metadata cannot be read.
- Widget state was reset by rerunning cells.

### Notes

No additional callable notes are documented.

### Example

```python
Not documented yet
```

### Public callable source code

- Source file path: `src/fabricops_kit/governance_review.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L300-L341">View widget_select_catalogue_table on GitHub</a>

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

## Internal implementation summary

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

??? info "Internal helpers used: 6"

    This callable uses 6 internal helpers for metadata loading and other.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_build_metadata_table_key</code>, <code>_catalogue_table_options</code>, <code>_stable_metadata_key</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_rows</code>, <code>_is_success</code>, <code>_value</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Metadata loading helpers"

            **`def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L77-L78)

            ```python
            def _build_metadata_table_key(environment_name, dataset_name, table_name) -> str:
                return _stable_metadata_key(environment_name, dataset_name, table_name)
            ```

            **`def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L221-L270)

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

            **`def _stable_metadata_key(*parts: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L72-L74)

            ```python
            def _stable_metadata_key(*parts: Any) -> str:
                normalized = "|".join(str(part or "").strip().lower() for part in parts)
                return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            ```

        ??? example "Other helpers"

            **`def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L62-L67)

            ```python
            def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
                if rows_or_df is None:
                    return []
                if hasattr(rows_or_df, "collect"):
                    rows_or_df = rows_or_df.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]
            ```

            **`def _is_success(row: dict[str, Any]) -> bool`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L74-L75)

            ```python
            def _is_success(row: dict[str, Any]) -> bool:
                return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES
            ```

            **`def _value(row: dict[str, Any], name: str, default: Any='') -> Any`**

            Source: [`src/fabricops_kit/governance_review.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L70-L71)

            ```python
            def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
                return row.get(name, row.get(name.upper(), default))
            ```


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
- Source line: `300`
- Inbound references count: 0
- Outbound references count: 3
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

- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.governance_review._catalogue_table_options`
- `fabricops_kit.governance_review._coerce_rows`

### Raw source metadata

- Source file path: `src/fabricops_kit/governance_review.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L300-L341">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/governance_review.py#L300-L341</a>
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

- Internal helper count: 6
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
