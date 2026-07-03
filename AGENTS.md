# AGENTS.md

## Purpose

Canonical operating guide for Codex/agent contributions in this repository. Keep contributions reusable, public-safe, and easy to hand over to junior engineers.

## Core operating rules

- Pull requests must target `main`.
- Treat GitHub as the source of truth.
- Treat Microsoft Fabric as the execution runtime.
- Keep AI in the loop and optimize for junior-friendly handover.
- Prefer small, focused PRs over broad restructures.
- Prefer updating existing files/modules; add new files only when clearly justified.
- Do not add backwards-compatibility aliases, legacy parameter names, or
  transitional behavior unless the PR explicitly asks for migration support.
  Prefer clean APIs and update notebooks/docs/tests to the new contract.
  When a PR intentionally replaces a model, remove old metadata fields and
  docs language too; do not preserve old names as compatibility columns unless
  explicitly requested.
- Keep metadata responsibilities separated: `METADATA_DATA_CATALOGUE` stores observed table and column profiles, `METADATA_GUARDRAIL_RULES` is approved
  guardrail intent, and `METADATA_GUARDRAIL_RESULTS` is runtime outcomes.


## Function architecture rules

- Public functions use non-underscore names and are notebook-facing or user-facing API entrypoints.
- Internal functions use non-underscore names and are architecture-visible implementation units.
- Private helper functions use leading underscores and are hidden implementation details, but they may appear in dedicated review-only cleanup inventories.
- New architecture-visible internal functions must not be created with leading underscores.
- New underscore-prefixed functions must be private helpers only.
- Public functions must not call other public functions.
- Internal functions must not call public functions.
- Public and internal functions may call their own private helpers.
- Classes, dataclasses, enums, constants, protocols, config objects, and external libraries are supporting objects, not architecture layers.
- Private helpers are not Public/Internal architecture layers and must be labelled as review-only private helpers when surfaced.
- Public API Surface KPI counts must not include private helpers or mix private-helper counts into Public/Internal function totals.
- New dashboard metrics must be public-callable-centric unless explicitly marked as internal/debug.
- Coding agents must update tests and snapshots whenever architecture classification or dashboard outputs change.

## Public callable package file pattern

When adding any new public callable function, follow the FabricOps public
function architecture pattern: one public owner file named after the function,
one package `shared.py` for helpers/classes/dataclasses/value objects, and
`__init__.py` for exports. Do not add `public.py`, `models.py`,
`classes.py`, adapter/resolver files, or compatibility shims unless explicitly
approved. See `docs/reference/public-function-architecture.md`.

## Fabric IO callable file pattern

- Notebook-facing Fabric IO public callable files live under `src/fabricops_kit/io/` with one public callable per owner file.
- Reusable Fabric IO implementation helpers live in `src/fabricops_kit/io/shared.py`.
- The preferred Fabric IO call path is: public callable file -> `fabricops_kit.io.shared` internal helper -> same-file private helper.
- Same-file private helpers may use leading underscores when they improve readability.
- Cross-file calls or imports of underscore-prefixed private helpers are architecture violations. Promote reused helpers to non-underscored internal helpers in the domain owner file instead.
- Do not add wrapper-on-wrapper IO layers. Fabric IO public callable files should use `src/fabricops_kit/io/shared.py` directly for shared implementation behavior.
- Do not keep legacy IO modules or private compatibility wrappers after their callers move to the real owner module. Delete unused modules and helpers after migration.
- Do not add or keep IO compatibility shims for unsupported private helper imports. Delete unused private helpers after migration.

## Before opening a PR

- Run the architecture guardrail tests that validate source code directly.
- Run dashboard snapshot tests when the PR intentionally changes dashboard behavior, generated-reference outputs, or generated-reference snapshot expectations.
- Treat generated reference validation as optional unless the PR is explicitly a reference/docs refresh or changes generator/dashboard/reference-contract logic.
- When changing `scripts/generate_function_reference.py`, dashboard rendering, embedded call-graph contracts, architecture classification, callable inventory/public flow generation, or tests that intentionally assert generated output, update relevant tests and verify the generator works locally or in CI.
- Confirm no new underscore function is surfaced as an Internal function.
- Confirm no private helper appears in Public API Surface KPIs.
- Confirm public-to-public calls are not introduced.
- Confirm internal-to-public calls are not introduced.
- Confirm public notebook-facing API behavior is intentionally preserved or explicitly documented as breaking.

## Public safety and positioning

- Keep all examples and guidance generic and public-safe.
- Never include real data, secrets, tenant/workspace identifiers, internal URLs, or production screenshots.
- Public brand name: **FabricOps Starter Kit**.
- Preferred positioning: **governed, quality-checked, Microsoft Fabric notebook workflows**.
- Do not position this project as a full data product platform.

## Documentation and API reference rules

- Keep root `README.md` concise and navigation-focused.
- Put lifecycle/operating behavior in `docs/`.
- Put callable API reference guidance in `src/README.md`.
- Do not maintain duplicate manual callable/member lists across README/docs pages.
- Public callable docs are sourced from `src/fabricops_kit/` docstrings plus source metadata.
- `docs/reference/*`, `docs/api/modules/*`, and related navigation are generated artifacts.
- Do not manually treat generated docs as source of truth; source code, docstrings, `__all__`, and reference metadata remain the source inputs.
- Routine implementation changes to existing functions do not require running `scripts/generate_function_reference.py`.

## Generated reference artifacts and Codex runs

Codex source PRs should stay focused on source changes. Generated reference
files are built during the docs/GitHub Pages workflow, which runs the generator
before MkDocs builds the site.

- Agents must not manually edit generated reference outputs as source of truth.
- Ordinary source PR: do not commit generated reference artifacts; the docs
  build regenerates them before deployment.
- Generator/dashboard/reference-contract PR: when changing
  `scripts/generate_function_reference.py`, dashboard rendering logic, embedded
  call-graph data contracts, architecture classification, callable inventory or
  public flow generation, or tests that intentionally assert generated
  dashboard/reference output, update relevant tests and verify the generator
  works locally or in CI.
- GitHub Pages/docs builds must run
  `PYTHONPATH=src python scripts/generate_function_reference.py` before
  `mkdocs build` so the dashboard and reference files are produced in the build
  workspace before the site artifact is built.

Avoid these generated files and folders in normal Codex source PRs:

- `docs/assets/function-call-graph-dashboard.html`
- `docs/reference/_data/`
- `docs/api/reference/`
- `docs/api/modules/`
- `docs/reference/index.md`
- `mkdocs.yml` reference/module navigation when changed only because of
  generation

### Generated artifact boundaries

Keep source changes, generated reference refreshes, dashboard builds, and docs
wording changes as separate PRs by default.

- Do not regenerate or commit generated artifacts unless the PR is explicitly
  scoped as a generator, reference refresh, or dashboard build refresh PR.
- Backend generated artifacts include call graph JSON, export JSON, reference
  JSON, snapshots, generated API reference output, generated navigation, and
  generated docs.
- Frontend generated artifacts include dashboard HTML, built dashboard bundles,
  static dashboard output, and other compiled frontend artifacts.
- Backend/source PRs should not touch dashboard HTML, frontend build output, or
  frontend-only source unless explicitly required.
- Frontend/source PRs should not regenerate backend JSON, backend reference
  artifacts, snapshots, generated API reference output, or generated navigation
  unless the backend contract is intentionally changed.
- If generated artifacts become stale after a source change, mention the needed
  refresh in the PR summary instead of committing generated diffs.

### CI and generated artifact policy

CI may run backend generation, frontend builds, or dashboard builds as validation
steps, but validation builds must not be treated as source-of-truth repository
updates.

A PR build or GitHub Pages deployment can prove that generated output still
builds, but it does not refresh the generated artifacts stored on `main` unless
those generated files are explicitly committed in a scoped refresh PR.

Do not rely on GitHub Pages deployment output as evidence that `main` contains
fresh generated JSON, dashboard HTML, snapshots, navigation, or API reference
output.

If a source PR makes generated artifacts stale, mention the required refresh in
the PR summary instead of committing generated diffs.

Use separate explicit refresh PRs for:

- Backend reference/export regeneration.
- Frontend/dashboard build output regeneration.
- Docs wording-only updates.

### When generated references are required

Generated references are refreshed by the docs/GitHub Pages build. Run the
generator locally or in CI when validating generator/dashboard/reference-contract
changes; do not manually edit generated outputs.

Generator validation command:

```bash
PYTHONPATH=src python scripts/generate_function_reference.py
```


## Generated reference symbols and artifacts

Do not manually edit generated reference outputs as source of truth. Update source inputs/generator first, then regenerate when a release or public API/reference change requires it.

Generated artifacts:
- `docs/assets/function-call-graph-dashboard.html`
- `docs/reference/index.md`
- `docs/reference/_data/dependency-metadata.json`
- `docs/reference/call-graph.md`
- `docs/api/reference/*.md`
- `docs/reference/internal/*.md`
- `docs/api/modules/*.md`
- `mkdocs.yml` reference/module navigation

Source inputs:
- `src/fabricops_kit/**/*.py`
- `src/fabricops_kit/__init__.py::__all__`
- `src/fabricops_kit/docs_metadata.py`
- `scripts/generate_function_reference.py`

## Interactive widget API rules

- Public interactive widget functions must begin with `widget_`.
- Use `widget_<verb>_<object>`.
- Import IPython display with `from IPython import display as ip`.
- Use `ip.display(...)` for widgets.
- Preserve unqualified `display(...)` for Fabric-native DataFrame rendering.
- Do not create duplicate wrapper functions for an existing widget workflow.

## Public API docstring requirements

For new/modified public APIs in `src/fabricops_kit/` (public functions/classes/dataclasses/important methods):

- Use complete **NumPy-style** docstrings.
- Include relevant sections (`Parameters`, `Returns`, and when needed `Raises`, `Notes`, `Examples`, `See Also`).
- Describe actual behavior (no placeholder text).
- Do not mix Google-style `Args`/`Returns` headers with NumPy-style headers.
- For Fabric-specific behavior, document runtime assumptions in `Notes`.
- Internal-only modules should not appear as public modules unless clearly labeled internal-only.
- Deprecated callables must not be promoted as the recommended path when a replacement exists.
- New public callables must be added to `__all__`, have useful NumPy-style docstrings, and appear in generated reference docs.

### Ruff docstring linting

The active `pyproject.toml` Ruff configuration selects Ruff `D` docstring rules
globally. This is a repository lint rule, not personal preference.

- New or modified public functions need complete NumPy-style docstrings.
- When a `Parameters` section is present, every parameter in the function
  signature must be documented.
- Multiline docstring sections need blank lines between sections and after the
  final section body.
- Tests are linted too, so new public test functions need concise docstrings
  unless the Ruff configuration is intentionally changed.


Compact NumPy-style example:

```python
def api_name(param: str) -> bool:
    """Return whether `param` is valid.

    Parameters
    ----------
    param : str
        Value to validate.

    Returns
    -------
    bool
        True when valid.
    """
```

## Metadata lakehouse routing (required)

Do not assume attached/default lakehouse for metadata tables.

Always route metadata reads/writes via the `00_env_config` metadata target:

- `read_lakehouse_table(CONFIG, env, "metadata", "<metadata_table>")`
- `write_lakehouse_table(df, CONFIG, env, "metadata", "<metadata_table>", mode="append")`
- `CONFIG.path_config.paths[env]["metadata"]` for helpers needing metadata path/store

Applies to all `METADATA_*` tables (including future additions).

## What to update when changing X

### 1) `src/` function or public API change

- For routine implementation changes to existing functions, update tests/docs as needed; generated reference docs are not required.
- For public contract/catalogue/reference changes, update `src/fabricops_kit` public API docstrings (NumPy style) and intentional exports in `src/fabricops_kit/__init__.py::__all__`.
- Do not regenerate reference/module docs in normal source PRs, even for source changes that may make generated artifacts stale.
- Note any needed generated-docs refresh in the PR summary so the merge/release/reference-refresh path or a dedicated generated-docs PR can update generated artifacts separately.

### 2) Docs-only change

- Keep root `README.md` concise; place detailed lifecycle/operations content in `docs/`.
- Avoid duplicating manual callable lists that should be generated.

### 3) Notebook template change

- Keep templates public-safe and Fabric-runtime aware.
- Reuse canonical defaults from `src/fabricops_kit/` instead of duplicating constants inline.
- Keep examples runnable and teachable.

### 4) Generated reference change

- Update source metadata, tests, or generator logic first; do not manually edit
  generated markdown, JSON, dashboard HTML, or navigation as source of truth.
- Run or validate `PYTHONPATH=src python scripts/generate_function_reference.py`
  locally or in CI.
- Do not commit generated reference artifacts in ordinary source PRs; the
  docs/GitHub Pages workflow regenerates them before MkDocs builds the site.
- For generator/dashboard/reference-contract PRs, validate that generated
  timestamps or embedded data change when expected.

### 5) Metadata/lakehouse routing change

- Verify metadata operations use configured metadata target from `00_env_config`.
- Remove/avoid default-lakehouse references for metadata reads/writes.


## Optional validation checks

Duplicate adjacent docstring check:

```bash
python - <<'PY'
import ast
from pathlib import Path

bad = []
for path in Path("src/fabricops_kit").glob("*.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if len(body) >= 2:
                first = isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str)
                second = isinstance(body[1], ast.Expr) and isinstance(body[1].value, ast.Constant) and isinstance(body[1].value.value, str)
                if first and second:
                    bad.append(f"{path}:{node.lineno} {node.name} has duplicate adjacent docstrings")
if bad:
    raise SystemExit("\n".join(bad))
print("No duplicate adjacent docstrings found.")
PY
```

## Minimum validation before PR

Run these checks for normal source PRs:

- `uv run python -m compileall src tests`
- `uv run python -m pytest -q`
- `uv run ruff check .`

Do not include `scripts/generate_function_reference.py` as a normal validation
command.

## Glossary-backed documentation wording

- Use `docs/reference/_data/glossary.json` as the source of truth for user-facing FabricOps, governance, Microsoft Fabric, data engineering, file/configuration, and metadata table terminology.
- Use canonical glossary terms in narrative docs and notebook markdown; use aliases only when needed for natural grammar or when documenting literal technical names.
- Do not introduce new glossary-like wording without adding a canonical entry or alias mapping in `glossary.json`.
- Prefer simple narrative terms such as profile, enrichment, guardrails, enforcement, metadata lakehouse, pipeline output, data agreement, data steward, governance review, and lineage.
- Avoid heavy implementation terms in narrative docs unless the page is explicitly documenting metadata tables, implementation details, or API-level precision.
- Keep glossary chips non-invasive: first meaningful occurrence per page or section, click/tap expandable, and never inside code blocks, signatures, file paths, URLs, raw SQL, JSON, YAML, table names, or notebook code cells.
