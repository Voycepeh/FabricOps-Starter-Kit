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
state = widget_data_contract(table_id="table-orders")
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
| `context` | `Any` | No | `None` | FabricOps runtime context normally established by ``00_env_config``. |

</div>

## Returns

dict
    Current selector, editor, lifecycle state, and callable authoring actions.

### Return interpretation

The returned state remains pinned to the draft created or reopened for the requested table_id and active workspace; saves delegate to contract-authoring services.

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
versions are review-only. Grain description, selected key combination, and
optional enforcement are independent. Enabling Grain defaults to Block.
The sidebar shows the shared configured rules for Read and Write; it does
not execute validation. Rule buttons open the existing authoring controls.
DQ authoring uses Warn/Block and accepted failure rate percent.
Completeness counts missing rows; Uniqueness counts all duplicate-group rows.
Legacy distinct-key limits retain their runtime meaning and require an explicit
failure rate when edited.
Allowed values, range, pattern, relationship, and custom row rules can use
maximum failure percent. Conditional rules use matching applicable rows;
null values ignored by value checks are not counted as passing rows.
Prohibited-value lists remain strict. Required/Schema, Grain, Sensitive
Data, Freshness, and Source Drift do not gain a DQ row-percentage setting.
Actual violation counts remain visible even when within the authored limit.
If the notebook runtime cannot provide AI suggestions, AI actions are disabled
for the widget session while manual authoring remains available. Technical
failure details are retained in the returned state rather than shown in the editor.
When enabled through ``GOVERNANCE_CONFIG.ai_enrichment`` in ``00_env_config``,
Sensitive Data AI assesses canonical columns as Direct PII, Indirect PII, or
Not PII from governed metadata and profile evidence. Editable draft state remains
separate until Governance accepts a suggestion. Manual Description or Classification
edits mark dependent advice stale for explicit re-run. AI never saves, freezes,
activates, or enforces a contract; runtime Sensitive Data enforcement remains deterministic.
Sensitive Data offers Mask for categorical/text columns, Bucket for numeric
columns, and Tokenize/Remove for either. Dates offer Tokenize/Remove; complex
types offer Remove. Text defaults to full masking; partial preservation is optional.
Numeric buckets use approved fixed ranges or an anchored interval width.
Text grouping and distribution-derived boundaries belong in Engineering
exploration and transformations. AI suggestions receive governed metadata,
profile summaries including min/max, and the three most frequent values.
Treatment failures always block.

</div>

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Spark is resolved automatically from the existing execution session.
No session is created; Spark-dependent work raises
``RuntimeError`` when no session is available.

</div>

## See also

No related guides documented.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_data_contract.py:647`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_data_contract.py#L647-L5978">View on GitHub</a>
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
