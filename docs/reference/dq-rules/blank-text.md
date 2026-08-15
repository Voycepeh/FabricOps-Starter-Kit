# blank_text

## What this rule does

Checks that selected string columns are not null, blank, or whitespace-only.

## When to use it

Use for names, descriptions, labels, codes, or other text fields that must contain visible content.

## Rule applies to

**Data applicability:** Profiled string or string-castable columns where nulls, blank strings, and whitespace-only values should all be treated as missing content.

**Example column(s) on this page:** `programme_name`

## Parameters

```yaml
rule_type: blank_text
columns: ["programme_name"]
severity: error
```

## Example rule definition

```yaml
rule_id: blank_text_example
rule_type: blank_text
columns: ["programme_name"]
severity: error
description: "Example approved metadata rule for blank_text."
```

Governance Review stores the same rule type and parameters in `METADATA_GUARDRAIL`, including `rule_parameters_json`.

## Sample input data

| programme_id | programme_name |
| --- | --- |
| P001 | Data Foundations |
| P002 |     |
| P003 | null |
| P004 | Analytics Basics |

## Rows that pass

| programme_id | programme_name | Why |
| --- | --- | --- |
| P001 | Data Foundations | Visible text is present. |
| P004 | Analytics Basics | Visible text is present. |

## Rows that fail

| programme_id | programme_name | Why |
| --- | --- | --- |
| P002 | (spaces) | Whitespace-only string. |
| P003 | null | Null text value. |

## Notes

- The value is cast to string and trimmed before checking for blank text.
- Use `missing_values` with `maximum_null_percent=0` when blank strings are acceptable but actual nulls are not.

## Related rules

- [`missing_values`](missing-values.md)
- [`required_when`](required-when.md)
