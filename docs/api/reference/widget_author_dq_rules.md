# `widget_author_dq_rules`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Render interactive manual DQ guardrail authoring controls.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_author_dq_rules.py:272`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_author_dq_rules.py#L272-L596">View on GitHub</a>
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
def widget_author_dq_rules(
    spark_session: Any,
    context: dict[str, Any] | None=None,
    rule_type: str='missing_values',
    selected_columns: Iterable[str] | None=None,
    parameters: Mapping[str, Any] | None=None,
    severity: str='warning',
    commit: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

>>> form = widget_author_dq_rules(spark_session=spark)

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark_session` | `Any` | Yes | Fabric Spark session used to resolve profiled targets and save DQ rules. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active ``FABRIC_CONTEXT``. |
| `rule_type` | `str` | No | Initially selected canonical DQ rule ID. |
| `selected_columns` | `Iterable[str] \| None` | No | Columns initially selected on the resolved target. |
| `parameters` | `Mapping[str, Any] \| None` | No | Initial values for the selected rule's dynamic parameter controls. |
| `severity` | `str` | No | Initial DQ failure severity. |
| `commit` | `bool` | No | Save the initial valid configuration immediately. |

## Returns

Notebook-facing state, records, display rows, or persisted metadata rows produced by the helper.

### Return interpretation

The widget returns mutable preview records; approved saves write guardrail rule intent to METADATA_GUARDRAIL.

## Raises / Errors

Raises validation, widget, Spark, or metadata routing errors when required inputs are missing or the configured metadata lakehouse cannot be read or written.

### Common failure causes

- Rule parameters are invalid for the selected DQ type.
- No applicable column is selected.
- The metadata target cannot be written.

## Notes

<div class="reference-docstring-notes" markdown="1">

Rule definitions drive column semantics, parameters, defaults, and validation.
Independent rules create one ``METADATA_GUARDRAIL`` row per selected column.
Grouped, conditional, and ordered-pair rules create one logical row and keep
their column relationship in ``rule_parameters_json``.

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
| Preview | 0.1.0 |
| Preview | 0.2.0 |


</details>
