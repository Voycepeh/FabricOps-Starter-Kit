# widget_author_dq_rules

## Call-flow summary

- Downstream callables: 63
- Shared helpers: 23
- Private helpers: 40

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=widget_author_dq_rules">Open focused call flow in dashboard</a>


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

Use in 02_pipeline after target selection when engineering needs to batch-create, edit, clear, or draft DQ guardrail rules.

Do not use for runtime DQ enforcement or catalogue profiling; use run_table_guardrails for execution and profile helpers for observed evidence.

Renders manual DQ authoring controls that produce editable guardrail rule intent rows under the selected table governance policy.


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

The widget returns mutable preview records; approved saves write guardrail rule intent to METADATA_GUARDRAIL_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- Rule suggestions cannot be parsed.
- Bypass reason is missing when bypass is requested.
- The metadata target cannot be written.

## See also

No related guides documented.
