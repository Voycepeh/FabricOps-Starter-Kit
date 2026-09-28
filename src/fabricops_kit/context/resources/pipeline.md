## Current canonical 02 pipeline contract

Treat the latest canonical `02_pipeline` template represented by this installed Context Layer as the target shell. Preserve this order exactly:

`Environment -> Data Contract -> Read -> Transform -> Write`

Stable migration surfaces:

- Preserve project-owned environment values and source/target configuration; move them into the corresponding current configuration surfaces rather than replacing them with examples.
- Put source configuration at the top of each Read block, before the first `pipeline_read()` call.
- Keep project-owned transformation/business logic isolated in the dedicated Transform cell between Read and Write. Do not bury it in FabricOps-owned read/write orchestration.
- Put target configuration at the top of each Write block, before target resolution, checks, and `pipeline_write()`.
- Preserve stable canonical cell IDs for Environment, Data Contract, Read, Transform, and Write surfaces when producing a notebook.
- Adapt FabricOps-owned orchestration to current public APIs and current call signatures. Review semantic changes; do not translate syntax blindly.

Recommended public APIs for this migration: `widget_select_data_contract`, `pipeline_read`, `check_schema`, `check_freshness`, `check_source_drift`, `check_dq`, `check_sensitive_data`, `check_guardrail_coverage`, `profile_table`, `resolve_table_id`, `pipeline_write`.

Use those APIs only where the target shell uses them. Do not infer that every API belongs in every project pipeline.
