# less_than_or_equal

## What this rule does

Checks that populated values are less than or equal to a threshold.

## When to use it

Use for maximum percentages, caps, limits, or service-level thresholds.

## Rule applies to

**Data applicability:** Numeric, date, or otherwise comparable profiled columns that must be no greater than a configured threshold.

**Example column(s) on this page:** `response_rate`

## Parameters

```yaml
rule_type: less_than_or_equal
columns: ["response_rate"]
value: 100
severity: error
```

## Example rule definition

```yaml
rule_id: less_than_or_equal_example
rule_type: less_than_or_equal
columns: ["response_rate"]
value: 100
severity: error
description: "Example approved metadata rule for less_than_or_equal."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| survey_id | response_rate |
| --- | --- |
| SV001 | 72 |
| SV002 | 100 |
| SV003 | 101 |
| SV004 | 45 |

## Rows that pass

| survey_id | response_rate | Why |
| --- | --- | --- |
| SV001 | 72 | Below maximum. |
| SV002 | 100 | Equal to allowed maximum. |
| SV004 | 45 | Below maximum. |

## Rows that fail

| survey_id | response_rate | Why |
| --- | --- | --- |
| SV003 | 101 | Above maximum. |

## Notes

- Null values do not fail this rule by themselves.
- Use `between` when the value also has a minimum.

## Related rules

- [`less_than`](less-than.md)
- [`between`](between.md)
