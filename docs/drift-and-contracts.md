# Drift & Contracts

Use this page when you need to verify that pipeline outputs remain aligned with approved contracts over time.

## What this section covers

- Schema and partition drift checks.
- Contract-aware change behavior.
- Evidence needed for governance-aware release decisions.

## Why this matters

Drift monitoring prevents silent regressions and helps teams decide whether to block, warn, or approve changes with explicit evidence.

## Practical operating pattern

1. Establish contract and baseline expectations.
2. Run drift checks in pipeline execution.
3. Record evidence and classify changes by policy.
4. Route blocking or review-required changes through governance workflow.

## Output expectations

- Clear pass/warn/block signal.
- Evidence rows linked to run context.
- Human-readable notes for handover and review.

## Need implementation details?

For module-level mechanics and API signatures, see:

- [Drift module (developer reference)](api/modules/drift.md)
- [Callable Function Reference](reference/index.md)
