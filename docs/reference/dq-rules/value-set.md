# value_set

Checks one column against an approved governed set. `mode` is `allow` or `block`.

For small, stable domains, author the values directly:

```json
{"rule_type":"value_set","columns":["status"],"mode":"allow","values":["Open","Closed"]}
```

For larger or centrally maintained domains, reference a governed Catalogue table column instead:

```json
{"rule_type":"value_set","columns":["cost_centre"],"mode":"allow","reference_table_id":"<catalogue table_id>","reference_column":"cost_centre"}
```

At runtime FabricOps resolves the `table_id`, reads the current distinct non-null values from the referenced Lakehouse or Warehouse column, and applies the same Allowed Values check. Inline values and a reference source are mutually exclusive.

Use a reference source when the approved domain is maintained as data rather than as contract configuration. The Data Contract stores the governed reference, not a copied list.
