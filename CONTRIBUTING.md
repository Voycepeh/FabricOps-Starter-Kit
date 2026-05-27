# Contributing

Thank you for contributing to **FabricOps Starter Kit**. This guide is for human contributors and AI agents.

## 1) Contribution philosophy

- Keep contributions public-safe, reusable, and notebook-practical for Microsoft Fabric.
- Keep PRs small and focused; prefer incremental changes over broad rewrites.
- Prefer updating existing modules/docs over adding new files unless a new user-facing concept is required.
- Align changes to the current workflow direction: source → unified → product movement, templates, reusable helper functions, and Fabric notebook execution.

## 2) Branch and PR workflow

- Base all work on `main`.
- Open PRs targeting `main`.
- Keep one concern per PR (code + required docs updates together).
- Treat GitHub state as the source of truth for review and merge decisions.

## 3) Code contribution rules

- Do not rename packages/modules/functions/folders/templates unless explicitly requested.
- Do not add duplicate modules for the same concern.
- Do not introduce backward-compatibility shims unless explicitly requested.
- Keep examples synthetic and tenant-safe (no private IDs, internal URLs, or production data).
- For public APIs, expose only intentional user-facing callables and keep API docs generated from source metadata.

## 4) Documentation contribution rules

- Keep root `README.md` concise; update it only when top-level navigation/journey must change.
- Put lifecycle/operating behavior in `docs/`.
- Keep callable API reference centered in `src/README.md` + generated docs.
- If template behavior or helper APIs change, update docs/templates in the same PR.
- Do not duplicate long content across files; link to the canonical doc.

## 5) Function and docstring standards

For new/changed public APIs under `src/fabricops_kit/`:

- Use complete **NumPy-style** docstrings (`Parameters`, `Returns`, and `Raises` where applicable; add `Notes`/`Examples` when helpful).
- Describe actual behavior (no placeholders).
- Keep notebook-friendly, public-safe examples.
- For Fabric-specific behavior, state runtime assumptions (Fabric runtime requirements, PySpark expectations, optional dependencies).
- If public functions are added/removed/renamed or registry mappings/docstrings change, regenerate reference docs:
  - `PYTHONPATH=src python scripts/generate_function_reference.py`

## 6) Testing expectations

Use existing repo commands (do not invent new tooling). Standard checks:

- `uv run python -m compileall src tests`
- `uv run python -m pytest -q`
- `uv run mkdocs build`

If a command is not available in your environment, report what you ran and why anything was skipped.

For local development setup and reproducibility:

- Run `uv lock` then `uv sync` to resolve and install dependencies from the committed lockfile.
- Run `uv run pytest tests` for default test execution.
- Run `uv run --python 3.11 pytest tests` and `uv run --python 3.12 pytest tests` to validate across supported interpreters.
- `.python-version` pins local development to Python 3.11, while `pyproject.toml` allows package usage on Python `>=3.11`.

## 7) Microsoft Fabric testing expectations

For changes that affect runtime behavior in Fabric:

1. Build the wheel from this repo.
2. Upload/install the wheel in the Fabric workspace environment.
3. Import the updated package in a Fabric notebook.
4. Run the relevant notebook template path and API checks for your change.
5. Verify expected outputs (tables/files/metadata artifacts) and document observations in the PR.

## 8) AI agent / Codex instructions

- Inspect current files before editing; prefer surgical diffs.
- Do not do broad rewrites unless explicitly requested.
- Keep names aligned with the current rebranded repo state.
- When changing public APIs/docs relationships, update generated references and related docs in the same PR.
- Keep PR summaries explicit about what changed, why, and how it was validated.

## 9) What not to do

- Do not rebrand or rename existing repo structures without explicit request.
- Do not include secrets, workspace identifiers, tenant-specific paths, or private screenshots.
- Do not modify unrelated files.
- Do not touch root `README.md` unless directly required.
- Do not claim tests were run if they were not.

## 10) PR checklist

- [ ] PR is based on `main` and targets `main`.
- [ ] Scope is small and focused.
- [ ] No unnecessary renames/restructures/backward-compat shims.
- [ ] Public API/docstring standards are met (NumPy-style, accurate, notebook-safe examples).
- [ ] Generated function reference docs were updated if public API surface or mappings changed.
- [ ] Docs/templates were updated where template or helper behavior changed.
- [ ] Local checks were run with available repo commands, or skips are explained.
- [ ] Fabric runtime validation steps were completed or explicitly marked N/A with reason.
