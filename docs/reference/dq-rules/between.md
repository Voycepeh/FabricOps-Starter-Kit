# between

## What this rule does

Checks that populated numeric or comparable values stay within a configured lower and/or upper bound.

## When to use it

Use for percentages, scores, quantities, and other values with a known valid range.

## Rule applies to

**Data applicability:** Numeric, date, or otherwise comparable profiled columns where catalogue min/max evidence should stay inside an approved lower and/or upper bound.

**Example column(s) on this page:** `score`

## Parameters

```yaml
rule_type: between
columns: ["score"]
min_value: 0
max_value: 100
severity: error
```

## Example rule definition

```yaml
rule_id: between_example
rule_type: between
columns: ["score"]
min_value: 0
max_value: 100
severity: error
description: "Example approved metadata rule for between."
```

Governance Review stores the same rule type and parameters in `METADATA_DQ_RULES`, including `rule_parameters_json`.

## Sample input data

| assessment_id | score |
| --- | --- |
| A001 | 88 |
| A002 | 0 |
| A003 | 104 |
| A004 | -2 |

## Rows that pass

| assessment_id | score | Why |
| --- | --- | --- |
| A001 | 88 | Inside range. |
| A002 | 0 | On inclusive lower bound. |

## Rows that fail

| assessment_id | score | Why |
| --- | --- | --- |
| A003 | 104 | Above maximum. |
| A004 | -2 | Below minimum. |

## Notes

- You may provide only `min_value` or only `max_value` when the rule has one-sided bounds.
- Null values do not fail this rule by themselves.

## Related rules

- [`greater_than_or_equal`](greater-than-or-equal.md)
- [`less_than_or_equal`](less-than-or-equal.md)
- [`date_between`](date-between.md)
