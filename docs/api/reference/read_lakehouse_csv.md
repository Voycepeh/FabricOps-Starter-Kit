# `read_lakehouse_csv`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Read a CSV file from a configured Fabric-resolved path through Spark CSV.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">00C_demo_setup</span>
</p>

## Usage notes

Use when reading a CSV file from a configured Fabric-resolved path.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
orders_df = read_lakehouse_csv("incoming/orders.csv", inferSchema=True)
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_csv(
    relative_path: str,
    *,
    store: str='Bronze',
    header: bool=True,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `relative_path` | `str` | Yes | `—` | Relative CSV file or folder path resolved underneath the configured Lakehouse ``Files`` area. |
| `store` | `str` | No | `'Bronze'` | Logical Lakehouse store key from ``00_env_config``. It is not necessarily the literal physical Lakehouse name. |
| `header` | `bool` | No | `True` | Whether Spark should treat the first row as column names. When ``header=True``, the first row is used as column names. When ``header=False``, the first row is treated as data and Spark typically creates generic column names such as ``_c0``, ``_c1``, and ``_c2``. |
| `context` | `dict[str, Any] \| None` | No | `None` | Active Fabric context override. |
| `**options` | `—` | No | `—` | Additional Spark CSV reader options passed directly to Spark's CSV reader, such as ``inferSchema``, ``sep``, ``quote``, ``escape``, ``encoding``, ``multiLine``, ``dateFormat``, ``timestampFormat``, ``nullValue``, ``mode``, and ``recursiveFileLookup``. FabricOps does not interpret or transform these options beyond forwarding them. |

</div>

## Returns

pyspark.sql.DataFrame
    A lazy Spark DataFrame representing the CSV file or compatible CSV
    files found at the resolved Lakehouse ``Files`` path. Column types
    follow Spark CSV reader behavior and generally remain strings unless
    schema inference or other schema handling is explicitly requested.

### Return interpretation

The returned DataFrame is a normal lazy Spark DataFrame until an action such as count, display, collect, or write is executed.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The lakehouse target or Files path cannot be resolved.
- The path is missing or the caller lacks read permission.
- Malformed rows, inconsistent files in a folder, absent headers, or empty files do not match the requested Spark CSV options.
- Schema inference can produce unexpected types; an explicit schema can mismatch source values.
- Some Spark failures appear only when a downstream action evaluates the DataFrame.

## Notes

<div class="reference-docstring-notes" markdown="1">

The Spark DataFrame is lazy; downstream actions evaluate the read. Additional
reader options are forwarded to Spark. Folder compatibility and malformed
record handling follow Spark CSV options.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

Use for a file, folder, or wildcard path. Columns remain strings unless
Spark schema inference or another schema strategy is requested.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_csv.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_csv.py#L10-L73">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 14 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared.get_default_fabric_context</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.resolve_fabric_context</code></li>
<li><code>fabricops_kit.io.shared._join_lakehouse_area_path</code></li>
<li><code>fabricops_kit.io.shared._validate_lakehouse_store</code></li>
<li><code>fabricops_kit.io.shared._validate_relative_path</code></li>
<li><code>fabricops_kit.io.shared._validate_warehouse_store</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
<li><code>fabricops_kit.io.shared.read_csv_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_configured_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_location</code></li>
<li><code>fabricops_kit.io.shared.resolve_lakehouse_file_path</code></li>
<li><code>fabricops_kit.io.shared.resolve_store</code></li>
</ul>


</details>
