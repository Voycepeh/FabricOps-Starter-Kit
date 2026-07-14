# `widget_author_dq_rules`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 62
- Shared helpers: 23
- Private helpers: 39

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=widget_author_dq_rules">Open Preview call flow</a>

Render interactive manual DQ guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_author_dq_rules.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_author_dq_rules.py#L15-L80">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Usage notes

Widget helpers provide a front-end notebook interface so users can enter metadata in a guided way.

They help users write values into the correct underlying metadata tables without manually editing those tables directly.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def widget_author_dq_rules(
    state: Mapping[str, Any],
    dq_authoring_mode: str='manual',
    rule_type: str='not_null',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
    spark_session: Any=None,
    context: dict[str, Any] | None=None,
    bypass_reason: str='',
    source_notebook_type: str='02_pipeline',
    created_by_role: str='engineering',
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

Example usage not documented yet.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `state` | `Mapping[str, Any]` | Yes | Guardrail target state returned by the target selector or prepared by a notebook workflow. |
| `dq_authoring_mode` | `str` | No | Authoring mode for the widget. The public widget supports manual rule authoring. |
| `rule_type` | `str` | No | Initial DQ rule type selected in the widget. |
| `selected_columns` | `Iterable[str] \| None` | No | Initial columns selected for the rule. |
| `parameters` | `Mapping[str, Any] \| None` | No | Initial rule parameters. |
| `severity` | `str` | No | Initial rule severity. |
| `spark_session` | `Any` | No | Fabric Spark session used when committing metadata rows. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. |
| `bypass_reason` | `str` | No | Governance-bypass reason used when applying rules immediately. |
| `source_notebook_type` | `str` | No | Notebook role recorded on authored metadata rows. |
| `created_by_role` | `str` | No | Actor role recorded on authored metadata rows. |
| `commit` | `bool` | No | When True, commit the selected rule instead of preview-only behavior. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns mutable preview records; approved saves write guardrail rule intent to METADATA_GUARDRAIL.

## Raises / Errors

Not documented yet

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- Rule suggestions cannot be parsed.
- Bypass reason is missing when bypass is requested.
- The metadata target cannot be written.

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

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 1:23 AM SGT
    Call-flow data generated: 14 Jul 2026, 9:32 PM SGT
