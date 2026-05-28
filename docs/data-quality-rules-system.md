# Data Quality Rules System

This page describes the **end-to-end operational loop** for DQ in FabricOps Starter Kit.

## End-to-end flow

1. **Profile data in `02_ex`** to collect quality and distribution evidence.
2. **Draft candidate DQ rules** (AI-assisted where useful) from profiling signals.
3. **Run human review/approval** so only approved rules become active policy.
4. **Persist approved rules** to governed metadata history.
5. **Load/enforce rules in `03_pc`** during deterministic pipeline execution.
6. **Write enforcement outputs**: pass/fail results, quarantine decisions, and run evidence.

In short: **profile → propose → approve → persist → enforce → evidence**.

## Why this matters

This loop keeps DQ both practical and governed:

- analysts can iterate quickly on candidate rules
- stewards/owners keep approval authority
- pipelines enforce only approved policy
- evidence remains traceable for audits and incidents

For callable/module details (for example draft, review, write, load, enforce helpers), use the API page for [`data_quality`](api/modules/data_quality.md).
