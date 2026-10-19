# uniqueness

## Where this appears in the Data Contract UI

**Columns → Column data quality → Uniqueness**

This is a directly authored column rule. The UI lets Governance set the minimum unique percentage; use 100% for strict uniqueness. Table-level composite DQ rules can also use this rule type. It is persisted as `guardrail_type: data_quality`, `rule_type: uniqueness`. Declared table Grain is a separate optional Guardrail; see [Grain enforcement](../../guided-demo/03-author-and-freeze-data-contract.md#grain-enforcement-and-the-orchestration-sidebar).

## What this rule does

Checks that one column, or one combination of columns, meets the required uniqueness level.

For a single column, you can require strict uniqueness or allow a minimum unique percentage. For example, `100` means every row must be unique, while `95` means the number of distinct values must be at least 95% of the row count.

## When to use it

Use for independent single-column or composite DQ uniqueness expectations. Author the table's declared row identity in Grain & Row Key.

## Data applicability

One or more columns that together define row identity.

## Parameters

Strict uniqueness:

```yaml
rule_type: uniqueness
columns: ["product_id"]
minimum_unique_percent: 100
```

Threshold uniqueness:

```yaml
rule_type: uniqueness
columns: ["product_id"]
minimum_unique_percent: 95
```

Composite DQ uniqueness remains strict by default:

```yaml
rule_type: uniqueness
columns: ["order_id", "line_id"]
```

If `minimum_unique_percent` is omitted, FabricOps defaults it to `100`.

## Example rule definition

```json
{"rule_type":"uniqueness","columns":["product_id"],"minimum_unique_percent":95}
```

## How the percentage is calculated

FabricOps calculates:

`distinct column combinations / total rows × 100`

If the percentage is below `minimum_unique_percent`, duplicate rows fail the rule.

## Notes

- Use `100` to mark a column as strictly unique.
- A lower percentage supports columns that should be mostly unique but may contain a small number of duplicates.
- Composite uniqueness is one table-level rule, not separate uniqueness checks per column.
- Profile distinctness can suggest a key candidate, but runtime validation proves uniqueness.
- `product_id + product_name` being unique does not prove `product_id → product_name`; that is a different relationship.
- Observed example pairs must not be converted into hard-coded allowed mappings unless Governance explicitly defines them.

## Related rules

- [`completeness`](completeness.md)
- [`column_relationship`](column-relationship.md)
