# Callable usage audit

Use this note when checking whether a public FabricOps helper is truly part of the notebook-facing surface.

## Count rule

The homepage callable count must match the approved package-root callable contract in `fabricops_kit.__all__`.

Current approved public callable count: **31**.

This is different from counting generated implementation helpers or historical reference pages. Internal helpers and removed legacy aliases must not be counted as reusable public callables.

## Usage rule

A callable is considered **used in a starter notebook** only when it is actively called in a notebook code cell, for example `run_table_guardrails(...)`.

Do not mark a callable as notebook-used when it is only:

- imported from `fabricops_kit`
- mentioned in markdown
- referenced by generated docs metadata
- called internally by another helper
- present as a removed legacy alias

## Schema guardrail example

`validate_schema` and `validate_schema_rule` are not public notebook-facing callables. Schema enforcement is still active, but it is now orchestrated through `run_table_guardrails(...)`, which calls internal runtime helpers.

Use `run_table_guardrails(...)` as the notebook-facing enforcement entry point instead of documenting the old schema helpers as public callables.
