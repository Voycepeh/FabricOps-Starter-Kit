# `widget_enrich_table_metadata`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render a consolidated column enrichment widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_enrich_table_metadata.py:14`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_enrich_table_metadata.py#L14-L50">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_review</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_review`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    spark_session: Any,
    context: dict[str, Any] | None=None,
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `guardrail_state` | `Mapping[str, Any]` | Yes | Guardrail target state containing table identity and catalogue profile rows for enrichment. |
| `spark_session` | `Any` | Yes | Fabric Spark session used when committing enrichment metadata rows. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. |
| `source_notebook_type` | `str` | No | Notebook role recorded on authored metadata rows. |
| `created_by_role` | `str` | No | Actor role recorded on authored metadata rows. |

## Returns

Widget state containing editable row controls, record builders, and a save callback for enrichment intent and classification metadata.

### Return interpretation

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT.

## Raises / Errors

Raises validation, widget, Spark, or metadata routing errors when selected target state is incomplete or the configured metadata lakehouse cannot be written.

### Common failure causes

- The selected guardrail target has no column-level evidence.
- Configured custom fields omit a field name.
- Metadata lakehouse writes cannot be routed through 00_env_config.

## See also

No related guides documented.


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |


</details>
