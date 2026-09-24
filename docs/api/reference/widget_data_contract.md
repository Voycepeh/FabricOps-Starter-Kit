# `widget_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create or reopen and author one agreement-free, table-centric Data Contract draft.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_data_contract.py:227`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_data_contract.py#L227-L1897">View on GitHub</a>
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
def widget_data_contract(
    table_id: str | None=None,
    contract_version: int | None=None,
    spark_session: Any=None,
    context: Any=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> state = widget_data_contract(table_id="table-orders", spark_session=spark)
>>> state["_controls"]["open_without_ai"].click()

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_id` | `str \| None` | No | Initial canonical governed table identity. If omitted, select it in the widget. |
| `contract_version` | `int \| None` | No | Initial exact lifecycle version. If omitted, the newest version is selected. |
| `spark_session` | `Any` | No | Active Microsoft Fabric Spark session. The configured session is used when omitted. |
| `context` | `Any` | No | FabricOps runtime context normally established by ``00_env_config``. |

## Returns

Exact-version state, compact controls, the displayed UI, and validation and freeze actions.

### Return interpretation

The returned state remains pinned to the draft created or reopened for the requested table_id and active environment; saves delegate to contract-authoring services.

## Raises / Errors

Raises validation, widget, Spark, or configured metadata routing errors.

### Common failure causes

- The table_id has no active Catalogue row.
- The metadata target cannot be read or written.
- A subtype-specific Guardrail value is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Saves delegate to canonical Enrichment and Guardrail services, then update the
in-memory governance snapshot and manifest without rereading unrelated metadata.
Lifecycle actions deliberately reload the snapshot. Profile context is lazy,
session-cached, read-only, and never added to the canonical payload. Scheduled
Refresh is discovered read-only from Microsoft
Fabric and remains independent of the authored Freshness expectation. Immutable
versions are review-only.
When enabled through ``GOVERNANCE_CONFIG.ai_enrichment`` in ``00_env_config``,
AI runs only after choosing Open with AI suggestions or an individual Run suggestion
action. Open without AI is the primary path and performs no AI Function calls.
Sensitive Data AI assesses canonical columns as Direct PII, Indirect PII, or Not PII
from governed metadata and profile evidence. Editable draft state remains
separate until Governance accepts a suggestion. Manual Description or Classification
edits mark dependent advice stale for explicit re-run. AI never saves, freezes,
activates, or enforces a contract; runtime Sensitive Data enforcement remains deterministic.

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


</details>
