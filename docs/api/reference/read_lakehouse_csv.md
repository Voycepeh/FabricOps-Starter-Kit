# `read_lakehouse_csv`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 9
- Private helpers: 6

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=read_lakehouse_csv">Open Live contract call flow</a>

Read a CSV file from a configured Fabric-resolved path through Spark CSV.

<div class="reference-docstring-intro" markdown="1">

Use ``read_lakehouse_csv`` for CSV data stored under the Lakehouse
``Files`` area. Use ``read_lakehouse_table`` for managed Delta tables
stored under the Lakehouse ``Tables`` area.

This function reads from the Lakehouse ``Files`` area, not a managed Delta
table in the ``Tables`` area. It can resolve either a single CSV file path
or a folder path, applies the ``header`` setting, forwards all additional
CSV reader options directly to Spark, and returns a lazy Spark DataFrame.
The resolved location is conceptually
``<configured lakehouse>/Files/<relative_path>``, which FabricOps maps to
the corresponding ABFSS path before delegating to Spark.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_csv.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_csv.py#L10-L104">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_csv(
    relative_path: str,
    target: str='source',
    spark_session=None,
    header: bool=True,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_df = read_lakehouse_csv("Files/inbound/student_enrolment/*.csv", target="source", header=True, inferSchema=True, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Relative CSV file or folder path resolved underneath the configured Lakehouse ``Files`` area. |
| `target` | `str` | No | Logical Lakehouse target from ``00_env_config``. It is not necessarily the literal physical Lakehouse name. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `header` | `bool` | No | Whether Spark should treat the first row as column names. When ``header=True``, the first row is used as column names. When ``header=False``, the first row is treated as data and Spark typically creates generic column names such as ``_c0``, ``_c1``, and ``_c2``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark CSV reader options passed directly to Spark's CSV reader, such as ``inferSchema``, ``sep``, ``quote``, ``escape``, ``encoding``, ``multiLine``, ``dateFormat``, ``timestampFormat``, ``nullValue``, ``mode``, and ``recursiveFileLookup``. FabricOps does not interpret or transform these options beyond forwarding them. |

## Returns

Spark DataFrame representing rows parsed from the selected CSV file or files. Columns and data types depend on the supplied schema and CSV reader options.

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

FabricOps resolves the configured Lakehouse Files path from
``00_env_config`` and then delegates to Spark's CSV reader with the supplied
options. Calling this function constructs a Spark read plan, and the file
scan occurs when a downstream action executes, such as ``display``,
``count``, ``collect``, or a DataFrame write. The function does not
immediately load the complete file into notebook memory.

Compact examples:

``df = read_lakehouse_csv("incoming/customers.csv", target="source")``

``df = read_lakehouse_csv("incoming/customers/", target="source")``

``df = read_lakehouse_csv("incoming/customers.csv", target="source", inferSchema=True)``

``df = read_lakehouse_csv("incoming/orders.csv", target="source", header=True, inferSchema=True, sep=",", encoding="UTF-8", mode="PERMISSIVE")``

When a folder path is supplied, Spark reads compatible CSV files from that
path into one DataFrame according to Spark CSV reader behavior. FabricOps
does not manually loop through or append files.

The function sets the ``header`` option and forwards the caller's CSV
options. It does not automatically infer data types. Unless the caller
requests schema inference or another schema strategy, Spark CSV columns are
generally read as strings. ``inferSchema=True`` can be passed through
``**options`` when inference is desired.

This function does not convert CSV data into a Delta table, write, move,
rename, or delete source files, register metadata, profile the returned
DataFrame, remove duplicate rows, standardize column names, infer schema
unless requested through Spark options, validate that every CSV file in a
folder has identical structure, apply custom malformed-record handling
beyond the supplied Spark CSV options, or automatically cache or persist
the returned DataFrame.

</div>

## See also

- [Templates](../../notebook-templates-implementation-guide/index.md)


<details>
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
<li><code>fabricops_kit.io.shared.resolve_target_store</code></li>
</ul>


</details>
