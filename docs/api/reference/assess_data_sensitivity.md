# `assess_data_sensitivity`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

Assess personal and non-personal data sensitivity using profile and verified governance evidence.


## Usage notes

Use after profiling, during Data Contract authoring, or when reviewing the actual output of a treatment.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
assessment = assess_data_sensitivity(profile_result, column_definitions={'salary': {'category': 'payroll'}})
```

</div>


<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def assess_data_sensitivity(
    profile_result,
    description=None,
    column_definitions=None,
    target_classification=None,
    use_ai=False,
    *,
    dataframe=None,
    sensitive_linkage=None,
    context=None,
) -> dict:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `profile_result` | `dict or pyspark.sql.Row` | Yes | `—` | A canonical column profile, a profile_table() result, or the profile_result from an orchestrated Read or Write. |
| `description` | `str` | No | `None` | Current business description of the selected column or dataset. |
| `column_definitions` | `mapping` | No | `None` | Column names mapped to draft descriptions or objects with a description and a configured category. |
| `target_classification` | `str` | No | `None` | A configured label. A lower target can produce treatment recommendations. |
| `use_ai` | `bool` | No | `False` | Request optional assistance when the configured Fabric AI endpoint is approved. |
| `dataframe` | `pyspark.sql.DataFrame` | No | `None` | Data within the assessed scope for explicit local detector and group checks. |
| `sensitive_linkage` | `bool` | No | `None` | Dataset evidence that sensitive information can (True) or cannot (False) be attributed to individuals or a sensitive group. Omit when unknown. A negative declaration does not override scan findings. |
| `context` | `dict` | No | `None` | Existing FabricOps notebook configuration and Metadata routing. |

</div>

## Advanced examples

<div class="reference-example-usage" markdown="1">

```python
assess_data_sensitivity(
    {"COLUMN_NAME": "amount", "DATA_TYPE": "decimal(12,2)"},
    description="Monthly staff base salary",
)["human_review_required"]
```

```text
True
```

</div>

## Returns

dict
    Findings include observed scope, nullable classification, approved
    dataset classification, minimum handling, review flags, provenance,
    and conditional treatments. The assessed classification describes the
    observed data. The approved classification remains a handling floor.

## Raises / Errors

ValueError
    If definitions, target classification, profile coverage, or scan scope are invalid.

## Behavior and scope

<div class="reference-docstring-intro" markdown="1">

Accept a table profile result, an orchestration profile result, or a single
column profile row. Column definitions can be descriptions or objects with
``description`` and a policy-defined ``category``. An optional Spark DataFrame
supplies explicit local scan evidence and must represent the assessed scope.
AI assistance requires opt-in and configured access. The returned findings
are advisory and preserve applicable minimum handling. Assessment does not
modify data, Contracts or classifications.

</div>

## See also

- [Sensitive data decisions](../../governance.md#sensitive-data-discovery-classification-and-treatment)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_contract/assess_data_sensitivity.py:113`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_contract/assess_data_sensitivity.py#L113-L458">View on GitHub</a>
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


</details>
