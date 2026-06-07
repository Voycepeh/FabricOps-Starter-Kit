# FabricOps Starter Kit skill

Use this skill when authoring notebooks, changing package helpers, or reviewing generated references for the FabricOps Starter Kit.

## Reference sources

Start with the existing generated function reference system. Do not replace it with a separate documentation or manifest system.

- `docs/reference/agent-manifest.json` — AI-oriented callable and helper execution metadata.
- `docs/reference/function-manifest.json` — machine-readable function inventory and dependency metadata.
- `docs/reference/callables/` — public callable pages for notebook authors.
- `docs/reference/internal/` — internal helper pages for package maintenance.
- `docs/reference/template-function-map.md` — notebook-template to callable map.

## Agent rules

- Respect `00_env_config`; use its configured environment and metadata targets rather than assuming an attached/default lakehouse.
- Prefer existing helpers before creating wrappers.
- Do not hardcode Fabric workspace IDs or item IDs unless explicitly provided by the user.
- Do not bypass metadata evidence when governance workflows require it.
- Check side effects before using a function.
- Use callable pages for notebook authoring.
- Use internal pages only for package maintenance.
- Update docs and tests together when changing public APIs, generated reference behavior, or notebook-facing guidance.

## Workflow

1. Identify the notebook or maintenance task.
2. Check `docs/reference/template-function-map.md` for the relevant starter flow.
3. Read the matching page in `docs/reference/callables/` before calling or recommending a public helper.
4. Inspect `docs/reference/agent-manifest.json` for required context, inputs, output, side effects, failure modes, verification, and related functions.
5. Use `docs/reference/internal/` only when maintaining package implementation details.
6. If source metadata, public API surface, or generator behavior changes, regenerate the existing reference outputs with `PYTHONPATH=src python scripts/generate_function_reference.py` and run relevant tests.
