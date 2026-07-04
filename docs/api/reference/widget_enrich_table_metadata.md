# widget_enrich_table_metadata

## Call-flow summary

- Downstream callables: 82
- Shared helpers: 28
- Private helpers: 54

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=widget_enrich_table_metadata">Open focused call flow in dashboard</a>


Render a consolidated column enrichment widget.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/widgets/widget_enrich_table_metadata.py:14`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/widgets/widget_enrich_table_metadata.py#L14-L50">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">03_governance</span>
</p>

**Used in notebooks:** `02_pipeline`, `03_governance`

## Usage notes

Use when governance reviewers need to enrich business context, sensitivity labels, PII classifications, and organization-specific fields for a selected profiled table.

Do not use to author DQ rules or enforcement intent; use the guardrail authoring and review widgets for enforceable DQ behavior.

Builds one editable enrichment row per selected profiled catalogue column and writes reviewed descriptive metadata without writing guardrail rules, guardrail results, or catalogue profiles.


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

The returned state can be inspected in tests or notebooks; invoking save appends rows only to METADATA_ENRICHMENT_RULES.

## Raises / Errors

Not documented yet

### Common failure causes

- The selected guardrail target has no column-level evidence.
- Configured custom fields omit a field name.
- Metadata lakehouse writes cannot be routed through 00_env_config.

## See also

No related guides documented.
