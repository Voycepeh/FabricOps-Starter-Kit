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

## Default task execution approach

Before implementing a substantial task, agents should resolve five items:

1. **Context** - repository area, source-of-truth files, current behavior, and relevant existing workflows.
2. **Task** - the smallest complete change that satisfies the request.
3. **Constraints** - explicit out-of-scope areas, public contracts, generated-artifact boundaries, and runtime assumptions.
4. **Expected output** - files or reports that should change, and files that must remain unchanged.
5. **Verification** - deterministic scripts, tests, builds, diffs, or manual checks needed to prove the outcome.

Prefer minimum-change engineering: inspect and reuse existing implementations before
creating new ones, update an existing owner file or workflow before adding a
parallel path, remove duplication instead of creating another maintained copy,
and avoid abstractions for hypothetical future use. Do not expand the requested
scope without a concrete repository need. Keep generated content generated. Use
deterministic scripts and tests for anything that can be checked mechanically;
use agent judgement for interpretation, planning, review, and changes that
cannot be fully encoded as deterministic checks.

## Backward compatibility and public contracts

Backward compatibility applies to supported public callables and externally
consumed data contracts. It does not require preserving private or shared
implementation structure.

For a Live public callable, preserve its externally observable contract unless
the task explicitly authorizes a breaking change. The public contract includes:

- public import path and exported name
- parameter names, order, defaults, and accepted inputs
- return type, schema, shape, and documented meaning
- documented side effects and persisted outputs
- documented exceptions and normal failure behaviour

The internal implementation may be replaced completely. Private helpers,
non-exported shared helpers, helper filenames, call chains, internal imports,
and internal algorithms may be renamed, moved, merged, split, inlined,
rewritten, deleted, or replaced with a different helper chain.

Do not preserve obsolete internal wrappers, aliases, adapters, resolver layers,
or transitional shims merely because internal implementation changed.

An unchanged function signature alone does not prove backward compatibility.
Verify observable behaviour, accepted inputs, return contracts, side effects,
persisted outputs, and failure behaviour.

Preview callables are not covered by Live backward-compatibility guarantees.
Preserve only behaviour required by the task and existing tests unless the task
explicitly promotes or freezes the callable.

Discontinued callables do not imply current support. Preserve historical
behaviour only when the task explicitly requires it.

When a task explicitly permits breaking cleanup, do not add compatibility
wrappers or deprecated aliases unless requested. Clearly identify every changed
public contract in the PR summary, and do not claim a change is non-breaking
merely because the signature is unchanged.


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

## Agent public call flow architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed public
callable architecture contract. Agents must use it to inspect public callable
scopes, callees, helper reachability, source locations, architecture
violations, cleanup/refactor signals, and defined-but-not-used functions before
changing function-level source code.

Use it as the public call-flow contract for planning and review, but do not
treat it as more authoritative than source code. If it conflicts with source
code, trust the source code and update/regenerate the contract through the
public call-flow generator.

Before changing a public callable, shared helper, private helper, callable
classification, or generated reference contract, agents should check the
relevant entries in `public-function-call-flows.json` to understand:

- public callable scopes
- direct and transitive callees
- helper reachability
- source locations
- architecture violations
- cleanup/refactor signals
- defined-but-not-used functions

When changing function-level source code, agents must run:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

Commit the regenerated `docs/reference/_data/public-function-call-flows.json`
when the change affects:

- callable structure
- source locations
- public exports
- helper relationships
- architecture classification
- public function flow metrics

Source code, `__all__`, reference metadata, and the generator remain the source
of truth. Do not manually edit `public-function-call-flows.json` as the fix. If
the JSON is wrong, fix the source or generator first, then regenerate the
contract.

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
- When changing split generators, dashboard rendering, embedded call-flow contracts,
  architecture classification, callable inventory/public flow generation, or tests
  that intentionally assert generated output, update relevant tests and verify
  the affected generator works locally or in CI.
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
- `docs/reference/*`, `docs/api/reference/*`, and related navigation are generated artifacts.
- Do not manually treat generated docs as source of truth; source code, docstrings, `__all__`, and reference metadata remain the source inputs.
- Function-level source changes must refresh the committed public callable
  architecture contract with
  `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py`;
  generated individual function pages remain docs workflow outputs unless the PR
  is explicitly scoped as a docs/reference refresh.

## Generated reference artifacts and Codex runs

Codex source PRs should stay focused on source changes. Generated reference
files are built during the docs/GitHub Pages workflow, which runs the generator
before MkDocs builds the site.

`docs/reference/_data/public-function-call-flows.json` is the committed public
callable architecture contract and preferred compact lookup index for agents.
It is useful for planning and review, but not authoritative over source code.

- Agents must not manually edit generated reference outputs as source of truth.
- Source code, `__all__`, reference metadata, and generators remain the source
  of truth for generated outputs. If generated JSON is wrong, fix those inputs
  first and regenerate.
- Ordinary source PR: do not commit generated individual function pages or
  dashboard HTML; the docs build regenerates those docs workflow outputs before
  deployment. When function-level source changes affect callable structure,
  source locations, public exports, helper relationships, architecture
  classification, or public function flow metrics, run the public call-flow
  generator and commit the regenerated
  `docs/reference/_data/public-function-call-flows.json` contract.
- Generator/dashboard/reference-contract PR: when changing split generators,
  dashboard rendering logic, embedded call-flow data contracts, architecture
  classification, callable inventory or public flow generation, or tests that
  intentionally assert generated dashboard/reference output, update relevant
  tests and verify the affected generator works locally or in CI.
- GitHub Pages/docs builds must run the split generators before `mkdocs build`
  so committed architecture data, dashboard files, and individual function
  reference pages are produced in the build workspace before the site artifact
  is built.

Avoid these generated files and folders in normal Codex source PRs unless the
PR is explicitly scoped as a docs/reference refresh:

- `docs/reference/_data/`
  - Exception: agents should read and, when function-level source changes
    affect the public call-flow contract, regenerate and commit
    `docs/reference/_data/public-function-call-flows.json`. Do not commit
    generated individual function pages or dashboard HTML for ordinary source
    PRs.
- `docs/api/reference/`
- `docs/reference/index.md`

### Generated artifact boundaries

Keep source changes, generated reference refreshes, dashboard builds, and docs
wording changes as separate PRs by default.

- Do not regenerate or commit generated artifacts unless the PR is explicitly
  scoped as a generator, reference refresh, or dashboard build refresh PR, or
  the PR changes function-level source code in a way that affects the committed
  `public-function-call-flows.json` architecture contract.
- Backend generated artifacts include the committed public call-flow JSON,
  generated individual function reference pages, reference indexes, generated
  navigation, and generated docs.
- Frontend generated artifacts include the public call-flow dashboard HTML, built
  dashboard bundles, static dashboard output, and other compiled frontend
  artifacts. Generated
  individual function pages and dashboard HTML are docs workflow outputs; do not
  commit them in ordinary source PRs unless explicitly scoped as a docs/reference
  refresh.
- Backend/source PRs should not touch dashboard HTML, frontend build output, or
  frontend-only source unless explicitly required.
- Frontend/source PRs should not regenerate backend JSON, backend reference
  artifacts, snapshots, generated API reference output, or generated navigation
  unless the backend contract is intentionally changed.
- If generated artifacts other than `public-function-call-flows.json` become
  stale after a source change, mention the needed refresh in the PR summary
  instead of committing generated diffs. Function-level source changes that
  affect the public call-flow contract must regenerate and commit
  `public-function-call-flows.json`.

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

If a source PR makes generated artifacts other than
`public-function-call-flows.json` stale, mention the required refresh in the PR
summary instead of committing generated diffs. Function-level source changes
that affect the public call-flow contract must regenerate and commit
`public-function-call-flows.json`.

Use separate explicit refresh PRs for:

- Backend reference/export regeneration.
- Frontend/dashboard build output regeneration.
- Docs wording-only updates.

### When generated references are required

Generated references are refreshed by the docs/GitHub Pages build. Run the
generator locally or in CI when validating generator/dashboard/reference-contract
changes; do not manually edit generated outputs.

Official generator commands:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
```


## Generated reference symbols and artifacts

Do not manually edit generated reference outputs as source of truth. Update source inputs/generator first, then regenerate when a release or public API/reference change requires it.

Current generator ownership model:

1. Committed architecture contract:
   - `docs/reference/_data/public-function-call-flows.json`
   - generated by:
     `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py`

2. Dashboard frontend:
   - `docs/assets/public-function-call-flows-dashboard.html`
   - generated by:
     `PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py`

3. Individual function reference pages:
   - `docs/api/reference/*.md`
   - `docs/reference/index.md`
   - `docs/function-call-graph.md`
   - generated by:
     `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py`

4. Standalone maintainer guide:
   - `docs/function-call-graph.md`
   - manually maintained and not generated by the individual reference generator

Source inputs and generators:
- `src/fabricops_kit/**/*.py`
- `src/fabricops_kit/__init__.py::__all__`
- `scripts/reference_docs_metadata.py`
- `scripts/generate_public_function_call_flows_json.py`
- `scripts/generate_individual_function_reference_pages.py`
- `scripts/generate_public_function_call_flows_dashboard.py`

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

- For function-level source changes, update tests/docs as needed and run
  `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py`.
- Commit the regenerated `docs/reference/_data/public-function-call-flows.json`
  when the change affects callable structure, source locations, public exports,
  helper relationships, architecture classification, or public function flow
  metrics.
- For public contract/catalogue/reference changes, update `src/fabricops_kit`
  public API docstrings (NumPy style) and intentional exports in
  `src/fabricops_kit/__init__.py::__all__`.
- Do not regenerate individual function pages, module docs, or dashboard HTML in
  normal source PRs, even for source changes that may make those generated
  artifacts stale.
- Note any needed generated-docs refresh in the PR summary so the
  merge/release/reference-refresh path or a dedicated generated-docs PR can
  update generated docs workflow outputs separately.

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
- Run or validate `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py`
  locally or in CI for reference-contract changes. Run
  `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py` for
  function-level source changes.
- Do not commit generated individual function pages, module docs, dashboard
  HTML, or navigation in ordinary source PRs; the docs/GitHub Pages workflow
  regenerates them before MkDocs builds the site. Commit
  `docs/reference/_data/public-function-call-flows.json` only when a
  function-level source change affects the public call-flow contract.
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

Do not include individual function page or dashboard generators as normal
validation commands unless the PR changes those generated docs workflow outputs.
