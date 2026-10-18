# `widget_data_contract`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Create or reopen and author one agreement-free, table-centric Data Contract draft.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">01_governance</span>
</p>

## Usage notes

Use as the primary UX for preparing and freezing one governed table’s next Data Contract version.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
state = widget_data_contract(table_id="table-orders", spark_session=spark)
state["refresh_manifest"]()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_data_contract(
    *,
    table_id: str | None=None,
    contract_version: int | None=None,
    spark_session: Any=None,
    context: Any=None,
) -> dict[str, Any]:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `table_id` | `str \| None` | No | `None` | Initial canonical governed table identity. If omitted, select it in the widget. |
| `contract_version` | `int \| None` | No | `None` | Initial exact lifecycle version. If omitted, the newest version is selected. |
| `spark_session` | `Any` | No | `None` | Active Microsoft Fabric Spark session. The configured session is used when omitted. |
| `context` | `Any` | No | `None` | FabricOps runtime context normally established by ``00_env_config``. |

</div>

## Returns

dict
    Current selector, editor, lifecycle state, and callable authoring actions.

### Return interpretation

The returned state remains pinned to the draft created or reopened for the requested table_id and active environment; saves delegate to contract-authoring services.

## Raises / Errors

ValueError
    If an identity, authored record, or lifecycle action is invalid.
RuntimeError
    If configured metadata routing or a lifecycle mutation fails.

### Common failure causes

- The table_id has no active Catalogue row.
- The metadata target cannot be read or written.
- A subtype-specific Guardrail value is invalid.

## Notes

<div class="reference-docstring-notes" markdown="1">

Save overwrites the complete canonical JSON for the selected draft version, then reloads
that exact version. A new draft is seeded from the previous frozen version when one exists.
Processing prefers the current Engineering Catalogue scan, otherwise the previous contract,
then defaults to overwrite. Catalogue-resolved processing is read-only; inherited, defaulted,
or manually saved processing remains editable until the draft is frozen.
Profile context remains read-only and is never added
to the canonical payload. Scheduled Refresh is discovered read-only from Microsoft
Fabric and remains independent of the authored Freshness expectation. Immutable
versions are review-only.
If the notebook runtime cannot provide AI suggestions, AI actions are disabled
for the widget session while manual authoring remains available. Technical
failure details are retained in the returned state rather than shown in the editor.
When enabled through ``GOVERNANCE_CONFIG.ai_enrichment`` in ``00_env_config``,
Sensitive Data AI assesses canonical columns as Direct PII, Indirect PII, or
Not PII from governed metadata and profile evidence. Editable draft state remains
separate until Governance accepts a suggestion. Manual Description or Classification
edits mark dependent advice stale for explicit re-run. AI never saves, freezes,
activates, or enforces a contract; runtime Sensitive Data enforcement remains deterministic.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_data_contract.py:525`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_data_contract.py#L525-L5446">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
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
| Preview | 0.2.5 |


</details>
