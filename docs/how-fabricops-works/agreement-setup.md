# 01 Agreement Setup

`01_agreement` is the agreement intake notebook. It records who owns the data relationship, what agreement applies, and which evidence supports that agreement before a pipeline uses it.

## Data steward intake

Use [`widget_render_data_steward`](../api/reference/widget_render_data_steward.md) to capture steward details. Steward rows give agreements an accountable owner and make later pipeline evidence easier to interpret.

## Agreement intake

Use [`widget_render_data_agreement`](../api/reference/widget_render_data_agreement.md) to define the agreement context. This is the contract context that `02_pipeline` later selects with its agreement selector, so keep names, scope, and ownership readable for notebook users.

## Agreement evidence

Use [`widget_render_agreement_evidence`](../api/reference/widget_render_agreement_evidence.md) to attach agreement evidence. Evidence makes the agreement more than a label: it gives later pipeline runs a traceable reason for why the selected contract exists.

## Handoff to `02_pipeline`

After agreement setup, `02_pipeline` can select the agreement and register the active notebook relationship. The pipeline then records run, lineage, and guardrail evidence against the selected agreement context instead of running as an isolated technical notebook.
