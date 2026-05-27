# Run Summary & Handover

Use this page when you need to close a FabricOps run with clear evidence and an operator-ready handover.

## What handover means in FabricOps

Handover is the operational continuity step between notebook execution and day-2 operation. It packages what ran, what was approved, what passed/failed, and what needs follow-up.

## Why this matters

- Keeps governance decisions visible for reviewers and downstream teams.
- Preserves execution evidence for audits and troubleshooting.
- Helps junior operators continue safely without reverse-engineering notebooks.

## What to include in run evidence

- Agreement/pipeline context and execution timestamp.
- Data quality outcomes and any blocked records/actions.
- Drift/schema check outcomes and decision notes.
- Metadata writes and approval state relevant to release decisions.
- Next actions and owner handoff notes.

## Recommended workflow

1. Execute notebook stages with approved metadata inputs.
2. Capture evidence artifacts during enforcement and checks.
3. Generate handover summary outputs for review.
4. Share handover with operational owners before promotion.

## Need implementation details?

For callable-level behavior and signatures, see developer docs:

- [Handover module (developer reference)](api/modules/handover.md)
- [Callable Function Reference](reference/index.md)
