# `widget_register_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Assemble and save a versioned Data Contract for one governed table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_register_data_contract.py:176`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_register_data_contract.py#L176-L371">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">01_governance</span>
</p>

**Used in notebooks:** `01_governance`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_register_data_contract(
    agreement_id: str | None=None,
    agreement_version: str | None=None,
    table_id: str | None=None,
    approved_usages: list[str] | None=None,
    target: str='metadata',
    schema: str | None=None,
    spark_session=None,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> state = widget_register_data_contract(
...     agreement_id="agreement-123",
...     agreement_version="2",
...     table_id="orders",
...     approved_usages=["analytics"],
...     target="metadata",
...     spark_session=spark,
... )
>>> state["save"]()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement_id` | `str \| None` | No | Saved parent Data Agreement lifecycle identity. |
| `agreement_version` | `str \| None` | No | Exact saved Data Agreement version. When omitted, the widget initially selects the latest saved version of ``agreement_id``. |
| `table_id` | `str \| None` | No | Initial active logical Catalogue table identity. |
| `approved_usages` | `list[str] \| None` | No | Initial usage subset. Every value must be approved by the Agreement. |
| `target` | `str` | No | Configured FabricStore target containing FabricOps metadata. |
| `schema` | `str \| None` | No | Metadata Lakehouse schema override. |
| `spark_session` | `object` | No | Spark session override. |
| `context` | `object` | No | FabricOps context, normally established by ``00_env_config``. |

## Returns

Mutable contract review state with structured governance context, completeness warnings, and an explicit save action.

### Return interpretation

review exposes the assembled governance context without HTML parsing; save appends exactly one draft contract version and does not mutate history.

## Raises / Errors

Raises when an agreement ID cannot be resolved or configured metadata cannot be read or safely written.

### Common failure causes

- No exact saved Agreement version is selected.
- The active environment has no active governed Catalogue tables.
- The metadata target cannot be written.

## Notes

<div class="reference-docstring-notes" markdown="1">

Rendering does not write metadata. Each explicit save appends exactly one
``draft`` row with ``is_active=False`` and the next version of a stable
contract identity derived from the Agreement lifecycle and ``table_id``.
The canonical payload freezes Agreement and steward context, current active
Catalogue structure and processing, current enrichment, active Guardrail expectations,
and the selected approved-usage subset. Runtime Guardrail result tables are
neither read nor embedded. Historical contract versions are never updated.
This workflow does not submit, approve, promote, export, or enforce a
contract and requires a configured Microsoft Fabric metadata Lakehouse.

</div>

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
| Preview | 0.2.0 |


</details>
