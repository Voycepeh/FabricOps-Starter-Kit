# FabricOps Starter Kit skill

Use this skill when authoring notebooks, changing package helpers, or reviewing generated references for the FabricOps Starter Kit.

## Reference sources

Start with the existing generated function reference system. Do not replace it with a separate documentation or manifest system.

- `docs/reference/agent-manifest.json` — AI-oriented callable and helper execution metadata.
- `docs/reference/function-manifest.json` — machine-readable function inventory and dependency metadata.
- `docs/reference/callables/` — public callable pages for notebook authors.
- `docs/reference/internal/` — internal helper pages for package maintenance.
- `docs/reference/dq-rules/` — generated DQ rule reference pages for supported rule types, parameters, and examples.
- `docs/reference/template-function-map.md` — notebook-template to callable map.

## Agent rules

- Respect `00_env_config`; use its configured environment and metadata targets rather than assuming an attached/default lakehouse.
- Prefer existing helpers before creating wrappers.
- Do not hardcode Fabric workspace IDs or item IDs unless explicitly provided by the user.
- Do not bypass metadata evidence when governance workflows require it.
- Check side effects before using a function.
- Treat `Not documented yet` as incomplete guidance; inspect source code, docstrings, and generated manifests before generating code.
- Use callable pages for notebook authoring.
- Use internal pages only for package maintenance.
- Update docs and tests together when changing public APIs, generated reference behavior, or notebook-facing guidance.
- Do not create a new documentation system or separate manifest for FabricOps guidance.
- Do not manually edit generated reference files unless the generator or source inputs require it.

## Workflow

1. Identify whether the task is agreement, profiling or review, pipeline enforcement, governance review, handover, or package maintenance.
2. Check `docs/reference/template-function-map.md` for the relevant starter flow.
3. Read the matching page in `docs/reference/callables/` before calling or recommending a public helper.
4. For DQ work, read the relevant generated DQ rule page in `docs/reference/dq-rules/` and the callable page before generating notebook code.
5. Inspect `docs/reference/agent-manifest.json` for required context, inputs, output, side effects, failure modes, verification, and related functions.
6. Use `docs/reference/internal/` only when maintaining package implementation details.
7. If source metadata, public API surface, or generator behavior changes, regenerate the existing reference outputs with `PYTHONPATH=src python scripts/generate_function_reference.py` and run relevant tests.

## Data quality and contract rules

Treat DQ rules as governed evidence, not ad hoc notebook checks. Rules should flow through the contract, profiling, review, approval, metadata, and enforcement lifecycle so downstream notebooks can explain which approved expectations were evaluated and why.

- Use `widget_review_dq_rules` for human review or approval workflows that draft, edit, approve, deactivate, or reactivate DQ rules.
- Use `enforce_dq_rules` for executable pipeline enforcement before target writes.
- Do not bypass approved metadata when pipeline enforcement requires reviewed rules; enforcement should read the approved active rules from the configured metadata target.
- Do not invent unsupported DQ rule types, syntax, parameters, or enforcement semantics.
- Inspect individual generated DQ rule pages before recommending rule syntax or parameters; summarize the relevant rule page instead of duplicating full generated rule content.
- Keep examples public-safe and generic; do not include production values, tenant or workspace identifiers, internal URLs, or screenshots.

Current supported DQ rule reference pages are generated under `docs/reference/dq-rules/`; use `docs/reference/dq-rules/index.md` as the source of truth. Current pages include:

- `docs/reference/dq-rules/accepted-values.md`
- `docs/reference/dq-rules/between.md`
- `docs/reference/dq-rules/column-a-gt-column-b.md`
- `docs/reference/dq-rules/column-a-gte-column-b.md`
- `docs/reference/dq-rules/column-pair-equal.md`
- `docs/reference/dq-rules/date-between.md`
- `docs/reference/dq-rules/date-not-future.md`
- `docs/reference/dq-rules/expression-true.md`
- `docs/reference/dq-rules/freshness.md`
- `docs/reference/dq-rules/greater-than.md`
- `docs/reference/dq-rules/greater-than-or-equal.md`
- `docs/reference/dq-rules/less-than.md`
- `docs/reference/dq-rules/less-than-or-equal.md`
- `docs/reference/dq-rules/max-age-days.md`
- `docs/reference/dq-rules/non-empty-string.md`
- `docs/reference/dq-rules/not-in-values.md`
- `docs/reference/dq-rules/not-null.md`
- `docs/reference/dq-rules/null-rate-below.md`
- `docs/reference/dq-rules/regex-match.md`
- `docs/reference/dq-rules/required-when.md`
- `docs/reference/dq-rules/unique.md`
- `docs/reference/dq-rules/unique-combination.md`
- `docs/reference/dq-rules/value-when.md`

For DQ requests:

1. Classify the work first: agreement, profiling or review, pipeline enforcement, governance review, or handover.
2. Read the matching callable reference, such as `docs/reference/callables/widget_review_dq_rules.md` for review/approval or `docs/reference/callables/enforce_dq_rules.md` for pipeline enforcement.
3. Read each relevant generated DQ rule page in `docs/reference/dq-rules/` before writing notebook code or recommending parameters.
4. Preserve the `00_env_config` metadata target route for reads and writes, especially for `METADATA_DQ_RULES` and related governed evidence tables.
5. If a requested rule cannot be mapped to a generated DQ rule reference page, explain that it is unsupported and propose the nearest supported rule only when the reference page confirms the syntax and parameters.
