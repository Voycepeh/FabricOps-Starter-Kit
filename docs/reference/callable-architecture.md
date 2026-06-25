# Callable Architecture Pattern

FabricOps public callables are optimized for notebook handover: a junior engineer should be able to open the public callable file, see the notebook-facing entry point, and follow shared implementation boundaries without hunting through a global utility hub.

## Preferred file pattern

Use this shape for new notebook-facing public callables and for incremental cleanup of migrated callables:

```text
Public callable file
→ domain shared helper file
→ same-file private helper
```

For IO callables, that means:

- **Public callable file**: keep each notebook-facing public callable in its own standalone file under `src/fabricops_kit/io/`, such as `read_lakehouse_csv.py`.
- **Domain shared helper file**: put reusable IO implementation helpers in `src/fabricops_kit/io/shared.py` when multiple IO callable files need the same behavior.
- **Same-file private helpers**: keep underscore-prefixed helpers private to the file that owns them.
- **No cross-file private calls**: do not import or call an underscore-prefixed helper from another file. If helper logic is reused across files, promote it to a non-underscored architecture-visible internal helper in the appropriate domain shared file.

## IO ownership direction

`src/fabricops_kit/io/shared.py` is the preferred shared implementation boundary for notebook-facing IO callables. New or migrated IO callable flows should avoid using `src/fabricops_kit/io_core.py` as the main implementation hub.

Treat `io_core.py` as a legacy compatibility and internal orchestration core only where existing metadata, governance, pipeline, or compatibility workflows still need it. Do not add new one-to-one public callable mirrors in `io_core.py`.

## Validation expectations

The callable architecture checks should continue to enforce these rules:

- Public callable → internal shared helper is allowed.
- Internal shared helper → same-file private helper is allowed.
- Same-file private helper usage is a warning or review signal, not a hard failure.
- Cross-file calls or imports of underscore-prefixed private helpers remain architecture violations.
- Public callables must not call other public callables.
- Internal helpers must not call public callables.

## Migration guidance

Prefer small migrations. Move one narrow helper or one callable flow at a time, keep public signatures unchanged, and add regression tests for notebook-facing behavior before widening the pattern.
