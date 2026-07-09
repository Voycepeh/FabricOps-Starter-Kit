# `widget_browse_metadata_catalogue`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 29
- Shared helpers: 17
- Private helpers: 12

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=widget_browse_metadata_catalogue">Open Preview call flow</a>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview |
| Live-critical dependencies | 0 |
| Direct Live dependents | 0 |
| Transitive Live dependents | 0 |


Render a searchable metadata catalogue browser.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_browse_metadata_catalogue.py:12`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_browse_metadata_catalogue.py#L12-L123">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_browse_metadata_catalogue(
    agreement: dict | None=None,
    agreement_id: str | None=None,
    agreement_version: str | None=None,
    target: str='metadata',
    schema: str | None=None,
    metadata_table: str='METADATA_DATA_CATALOGUE',
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement` | `dict \| None` | No | Agreement context used as a fallback for agreement and contract filters. |
| `agreement_id` | `str \| None` | No | Explicit agreement identifier. Takes precedence over ``agreement``. |
| `agreement_version` | `str \| None` | No | Explicit contract version. Takes precedence over ``agreement``. |
| `target` | `str` | No | Logical FabricStore target used to read the catalogue table. |
| `schema` | `str \| None` | No | Optional metadata lakehouse schema override. |
| `metadata_table` | `str` | No | Metadata catalogue table to read. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | Active FabricOps context override. |

## Returns

Mutable widget state whose dataframe key contains the currently filtered Spark DataFrame.

### Return interpretation

The returned state updates as selectors change; read state["dataframe"] for the currently filtered Spark DataFrame.

## Raises / Errors

Not documented yet

### Common failure causes

- No FabricStore targets are configured.
- The metadata catalogue table does not exist yet.
- The selected FabricStore target has no catalogue rows.

## See also

No related guides documented.


!!! info "Generated reference freshness"
    Reference pages generated: 08 Jul 2026, 1:08 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT
