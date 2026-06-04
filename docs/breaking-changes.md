# Breaking Changes

A breaking change is any change that can cause an existing FabricOps user to update package calls, notebook templates, metadata tables, configuration, runtime dependencies, or operational procedures before continuing safely.

## Breaking change categories

Treat the following as breaking-change candidates:

- function signature changes
- removed callable functions
- changed return values
- changed notebook required inputs
- changed notebook output behavior
- metadata column rename or removal
- metadata table rename or removal
- changed write behavior such as append versus overwrite
- required runtime or dependency changes
- changed configuration structure in `00_env_config` or an equivalent setup template

## Review expectations

Every breaking-change candidate should be documented in the release note with:

- affected callable, template, metadata table, or configuration surface
- user impact
- migration steps
- validation evidence
- rollback or compatibility guidance where practical

## Standard warning block format

Use this warning block in future release notes and migration pages when a release includes a breaking change.

!!! warning "Breaking change"
    **Affected surface:** `<callable, template, metadata table, or config area>`

    **What changed:** `<short description>`

    **User impact:** `<who is affected and what may fail>`

    **Migration required:** `<required user action before upgrade>`

    **Validation evidence:** `<tests, notebook runs, or maintainer review evidence>`

## Non-breaking documentation updates

Documentation-only additions are not breaking changes when they do not alter callable behavior, notebook required inputs, metadata output schemas, write behavior, dependency requirements, or configuration structure.
