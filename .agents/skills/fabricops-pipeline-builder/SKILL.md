---
name: fabricops-pipeline-builder
description: Build or update a Microsoft Fabric notebook pipeline in a consumer repository using an installed FabricOps Starter Kit release, from /start or a natural-language request.
---

# FabricOps Pipeline Builder

## Discover the project

Use this workflow when the agent supports `/start` for the skill, or when asked in natural language to build a FabricOps pipeline. On `/start` without a requirement, inspect the project and ask what the pipeline should do.

- Read the consumer's `AGENTS.md`, dependency declarations and lockfiles, existing pipeline items, and deployment instructions. Find the directory connected to Fabric Git and the intended development workspace. Check the installed version with `python -c "from importlib.metadata import version; print(version('fabricops-kit'))"` in the consumer's Python environment. Reuse the project's pin and Environment. If FabricOps is absent, use the team's approved wheel source and pin the version in its existing dependency workflow. The bundled example uses v0.5.0.
- Discover configured aliases, store types, schema conventions and the `00_env_config` deployment from existing configuration or the maintainer. Use only non-sensitive information in committed files, prompts and validation output. Fabric resolves physical workspace and item IDs in the runtime configuration. Confirm what each alias maps to and whether different aliases could refer to the same location.
- Match the [released 02_pipeline template and API reference](https://voycepeh.github.io/FabricOps-Starter-Kit/releases/) to the installed version. The example and operation checks use the v0.5.0 authoring conventions. Other releases need compatible behavior as well as signatures. If the installed release uses different authoring conventions for the requested behavior, explain the gap and ask for a supported alternative or an approved version change. Use the [current canonical notebook](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/02_pipeline.ipynb) to understand the structure.

## Resolve missing decisions

Ask only for information discovery and the request did not answer. Group related questions.

- **Source and destination.** Get the configured store aliases, physical table schemas and names, or Lakehouse Files paths and formats. For tables in schemaless stores use `schema=None`. For multiple targets, confirm one owning pipeline per target and whether independent publication is acceptable. Confirm the notebook name and Git folder when discovery leaves them ambiguous.
- **Transform and keys.** Confirm input/output columns, filters, joins, grain, and null handling where relevant. For latest-row deduplication, confirm the business key and an order that breaks ties deterministically. Distinguish transformation keys, incremental watermarks, and SCD processing keys.
- **Read and Write modes.** Confirm Full or Incremental Read per source and a Write strategy per target. Use the installed release's [Read & Write Modes](https://voycepeh.github.io/FabricOps-Starter-Kit/reference/read-and-load-strategies/) and callable docs. In v0.5.0, Incremental Read needs target store, schema and table coordinates and an explicit `read_parameters={"watermark_column": "..."}`. Pair Incremental Read with a compatible table Write. Ask for explicit Overwrite intent and complete input scope. For SCD1 require key columns, and for SCD2 require key columns and the effective column. Append New Only compares row hashes across runs. Choose SCD1 when the requirement is to update an existing business key. Files use Full Read and, where supported by the release, Overwrite or Append All Write.
- **Execution mode.** Default the review candidate to `Dry Run`. Use `Ungoverned` only when explicitly requested for an approved ungoverned target. For a Governed requirement, author a Dry Run candidate and document the existing Governance and Pipeline Promotion steps. Preserve the release's runtime admission gate. Git approval and an edited mode string cannot grant Governed authority.

If an essential alias, target, key, or mode choice remains unknown, show the missing decisions before producing a PR-ready notebook.

## Generate the Fabric item

Use the [Bronze-to-Silver example](examples/bronze_to_silver.Notebook/notebook-content.py) as a source scaffold. Preserve its five section headings for the validator, the Fabric cell headers and PySpark metadata, and the canonical lifecycle.

1. **Setup.** Import the five public entry points from `fabricops_kit`. Call `setup_notebook()` before `setup_pipeline(pipeline_mode=...)`, with the mode explicit. Use the workspace's configured `00_env_config`. Keep cross-workspace configuration and Environment attachment in the existing deployment workflow.
2. **Read.** Use a separate `orchestrate_read()` call for each source and retain each result, with the DataFrame available under `["dataframe"]`. Make store, coordinates and Read Mode explicit in the call. For SQL, confirm the read-only query and its physical source against the installed release. Register additional sources with their own Read calls.
3. **Transform.** Keep business logic in dedicated PySpark cells. For reviewability, keep operation settings literal in the Read and Write calls. Retain project-owned transformation logic when editing an existing pipeline.
4. **Write.** Pass the transformed DataFrame to `orchestrate_write()` with the explicit target, strategy and any required processing parameters. Route business I/O through the orchestrators. Use supported contract and processing settings as supplied and reviewed by the project. Keep raw storage writes and Governance mutations out of the notebook.
5. **Finalize.** Call `finalize_pipeline(pipeline)` after the operations, passing the session from Setup.

Use `<name>.Notebook/notebook-content.py` and a version 2 [`.platform` descriptor](examples/bronze_to_silver.Notebook/.platform) within the Fabric-connected folder. For a new item set `metadata.displayName` and create a new UUID for `config.logicalId` with `python -c "import uuid; print(uuid.uuid4())"`. Check uniqueness among the repository's Fabric items. Preserve the directory, logical ID and supported dependency metadata when updating an existing item. The Git logical ID is Fabric item metadata. FabricOps derives the Pipeline ID at runtime. Keep the actual configuration bindings in approved deployment resources. See [Microsoft's notebook Git guide](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment).

## Validate and prepare a PR

Run from the consumer root in its dependency environment. Supply every used store alias confirmed in the intended workspace, including any that appear only as Incremental target coordinates.

```sh
python .agents/skills/fabricops-pipeline-builder/scripts/validate.py \
  path/to/<name>.Notebook --store Bronze --store Silver --fabricops-version 0.5.0
```

Use the actual aliases and installed release in the command. Resolve failures before describing the result as PR-ready. Review the diff for real IDs, credentials, physical alias overlap, destructive writes, SQL scope, transformation assumptions and dependency changes. Static validation checks source code and declared aliases. Fabric validates actual store bindings, permissions, data, contracts and execution.

Report the artifact path, FabricOps version, sources and targets, Read and Write strategies, transformation/key decisions, execution mode, local validation command and result, and outstanding Fabric configuration or approval steps. Prepare the PR description and open a PR when requested. Use the consumer's normal review process before merging or syncing to Fabric.
