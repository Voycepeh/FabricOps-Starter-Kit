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
- Regenerate generated reference artifacts only when preparing a release, adding/removing/renaming public callables, changing `src/fabricops_kit/__init__.py::__all__`, changing callable/module ownership metadata, intentionally changing public callable documentation/API contracts, or intentionally refreshing the published API reference.

To refresh generated references when required:

```bash
PYTHONPATH=src python scripts/generate_function_reference.py
```


## Generated reference symbols and artifacts

Do not manually edit generated reference outputs as source of truth. Update source inputs/generator first, then regenerate when a release or public API/reference change requires it.

Generated artifacts:
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

- `read_lakehouse_table(CONFIG, env_name, "metadata", "<metadata_table>")`
- `write_lakehouse_table(df, CONFIG, env_name, "metadata", "<metadata_table>", mode="append")`
- `CONFIG.path_config.paths[env_name]["metadata"]` for helpers needing metadata path/store

Applies to all `METADATA_*` tables (including future additions).

## What to update when changing X

### 1) `src/` function or public API change

- For routine implementation changes to existing functions, update tests/docs as needed; generated reference docs are not required.
- For public contract/catalogue/reference changes, update `src/fabricops_kit` public API docstrings (NumPy style) and intentional exports in `src/fabricops_kit/__init__.py::__all__`.
- Regenerate reference/module docs only for release prep, public callable additions/removals/renames, `__all__` changes, callable/module ownership metadata changes, intentional public callable documentation/API contract changes, or intentional published API reference refreshes.
- Include generated docs updates in the same PR only when regeneration is required.

### 2) Docs-only change

- Keep root `README.md` concise; place detailed lifecycle/operations content in `docs/`.
- Avoid duplicating manual callable lists that should be generated.

### 3) Notebook template change

- Keep templates public-safe and Fabric-runtime aware.
- Reuse canonical defaults from `src/fabricops_kit/` instead of duplicating constants inline.
- Keep examples runnable and teachable.

### 4) Generated reference change

- Update source metadata/generator first (not generated markdown/json directly).
- Regenerate outputs and commit generated artifacts in the same PR.

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

Run relevant checks (at least for repo-wide hygiene PRs):

- `uv run python -m compileall src tests`
- `uv run python -m pytest -q`
- `uv run mkdocs build`

## Glossary-backed documentation wording

- Use `docs/reference/_data/glossary.json` as the source of truth for user-facing FabricOps, governance, Microsoft Fabric, data engineering, file/configuration, and metadata table terminology.
- Use canonical glossary terms in narrative docs and notebook markdown; use aliases only when needed for natural grammar or when documenting literal technical names.
- Do not introduce new glossary-like wording without adding a canonical entry or alias mapping in `glossary.json`.
- Prefer simple narrative terms such as profile, enrichment, guardrails, enforcement, metadata lakehouse, pipeline output, data agreement, data steward, governance review, and lineage.
- Avoid heavy implementation terms in narrative docs unless the page is explicitly documenting metadata tables, implementation details, or API-level precision.
- Keep glossary chips non-invasive: first meaningful occurrence per page or section, click/tap expandable, and never inside code blocks, signatures, file paths, URLs, raw SQL, JSON, YAML, table names, or notebook code cells.
