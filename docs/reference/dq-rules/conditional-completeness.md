# conditional_completeness

Requires a target column to be populated only when a condition on another column matches.

## Use it when

Use `conditional_completeness` for requirements of the form:

> When condition column matches a value, target column must be present.

Examples:

- "When status is Approved, approved_date is required."
- "When customer_type is Business, company_registration_number is required."

## Do not use it when

- The target is always required: use [`completeness`](completeness.md).
- The target must belong to an allowed set under the condition: use [`conditional_values`](conditional-values.md).
- The condition requires arbitrary multi-column logic that cannot be represented by this pattern: consider [`custom_expression`](custom-expression.md).

## Parameters

The condition supports `=` or `!=`. Set `treat_blank_as_missing` explicitly.

## Example

```json
{"rule_type":"conditional_completeness","columns":["status","approved_date"],"condition_operator":"=","condition_value":"Approved","treat_blank_as_missing":true}
```
