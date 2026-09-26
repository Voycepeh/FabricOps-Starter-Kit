# conditional_values

Checks a target column against a governed value set only when a condition on another column matches.

## Use it when

Use `conditional_values` for requirements of the form:

> When condition column matches a value, target column must be inside or outside an explicit set.

Examples:

- "When country is SG, currency must be SGD."
- "When account type is Internal, channel must not be External."

## Do not use it when

- The value set applies to every row: use [`value_set`](value-set.md).
- The target merely needs to be populated: use [`conditional_completeness`](conditional-completeness.md).
- The rule requires several independent conditions or mappings that cannot be represented without changing meaning: consider [`custom_expression`](custom-expression.md).

Profile frequencies are evidence only. Do not turn observed condition/value pairs into contractual mappings unless Governance explicitly states them.

## Parameters

The condition supports `=` or `!=`. `mode` is `allow` or `block`; `values` is a non-empty explicit governed list.

## Example

```json
{"rule_type":"conditional_values","columns":["country","currency"],"condition_operator":"=","condition_value":"SG","mode":"allow","values":["SGD"]}
```
