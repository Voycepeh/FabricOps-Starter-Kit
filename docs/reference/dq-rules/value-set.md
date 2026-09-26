# value_set

Checks one column against an explicit governed set.

## Use it when

Use `value_set` when Governance explicitly defines which values are allowed or blocked.

Examples:

- "Status must be Open, Closed, or Pending."
- "Country code must not be UNKNOWN or N/A."

## Do not use it when

- The values merely appeared in profiling or frequency evidence. Observed values are not automatically contractual.
- The allowed values apply only under another condition: use [`conditional_values`](conditional-values.md).
- The requirement is numeric or date bounds: use [`range`](range.md).

## Parameters

- `columns`: exactly one target column.
- `mode`: `allow` or `block`.
- `values`: non-empty explicit governed list.

## Examples

```json
{"rule_type":"value_set","columns":["status"],"mode":"allow","values":["Open","Closed","Pending"]}
```

```json
{"rule_type":"value_set","columns":["country"],"mode":"block","values":["UNKNOWN","N/A"]}
```
