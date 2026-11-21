# Build a FabricOps pipeline with an agent

Install the **FabricOps Pipeline Builder** skill in your data project and ask your coding agent to generate a Microsoft Fabric notebook. The project keeps its own transformations and Git history. FabricOps is installed as a dependency.

## 1. Prepare the consumer repository

Create an empty Git repository or open the one you already use for Fabric. Identify the branch and directory your development workspace will sync, for example `main` and `fabric/`. Keep the agent skill outside that directory when possible. Follow [Microsoft's Git integration setup](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started).

Reuse your project's pinned FabricOps release locally and in the Fabric Environment. For a new project trying the example, install the [v0.5.0 wheel](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/download/v0.5.0/fabricops_kit-0.5.0-py3-none-any.whl) in your Python 3.11+ environment and record the dependency in your project's usual format. Upload the same wheel as a custom library in the Fabric Environment. [Prepare a Fabric Environment](guided-demo/00A-prepare-fabric-artifacts.md).

## 2. Install the skill

From the consumer root, run this Bash snippet with a reviewed FabricOps commit SHA that contains the [skill](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/.agents/skills/fabricops-pipeline-builder). It downloads four files and leaves an existing installation in place.

```bash
(
  set -eu
  ref='REPLACE_WITH_REVIEWED_40_CHARACTER_COMMIT_SHA'
  [[ "$ref" =~ ^[0-9a-f]{40}$ ]] || { echo 'Set ref to the reviewed commit SHA.' >&2; exit 1; }
  skill=.agents/skills/fabricops-pipeline-builder
  [[ ! -e "$skill" && ! -L "$skill" ]] || { echo "Skill already exists at $skill" >&2; exit 1; }
  mkdir -p .agents/skills
  staging=$(mktemp -d .agents/skills/.pipeline-builder.XXXXXX)
  trap 'rm -rf "$staging"' EXIT
  base="https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/$ref/$skill"
  for file in SKILL.md scripts/validate.py \
    examples/bronze_to_silver.Notebook/.platform \
    examples/bronze_to_silver.Notebook/notebook-content.py; do
    mkdir -p "$staging/$(dirname "$file")"
    curl -fsSL "$base/$file" -o "$staging/$file"
  done
  python -c 'import os, sys; os.rename(*sys.argv[1:])' "$staging" "$skill"
)
```

Open a new agent session if skill discovery happens at startup. Invoke the **FabricOps Pipeline Builder** by name, use `/start` if the agent supports it for this skill, or point the agent to `.agents/skills/fabricops-pipeline-builder/SKILL.md`.

## 3. Describe the pipeline

For the Bronze-to-Silver example, use a request like this.

> Build a PySpark notebook named `bronze_to_silver` under `fabric/`. Full Read `Bronze.demo.order_events`. Drop events with a null `order_id`, `updated_at` or `event_id`. Keep the latest event per `order_id` by descending `updated_at`, breaking ties by descending `event_id`. The event ID is unique within each order. Keep `order_id`, `status` and `updated_at`. Prepare an SCD1 Write to `Silver.demo.orders` keyed on `order_id`. Use Dry Run for review.

The example assumes that the development workspace's `00_env_config` includes the following mappings. Configure the real workspace and item bindings privately. Use distinct schema-enabled Lakehouses for the demo source and target.

| Alias | Example binding |
| --- | --- |
| `Bronze` | Lakehouse `lh_demo_bronze`, source table `demo.order_events` |
| `Silver` | Lakehouse `lh_demo_silver`, target table `demo.orders` |
| `Metadata` | Centrally managed Metadata Lakehouse configured by Governance |

A source with the following rows yields `O-1 / shipped / 2026-01-02` for the prepared SCD1 Write. The input can use an integer `event_id` and a timestamp `updated_at`.

| order_id | updated_at | event_id | status |
| --- | --- | --- | --- |
| O-1 | 2026-01-01 00:00 | 101 | placed |
| O-1 | 2026-01-02 00:00 | 102 | packed |
| O-1 | 2026-01-02 00:00 | 103 | shipped |

SCD1 inserts new keys and updates matching keys when authorized to publish. A full input delivers the latest candidate for each order each time. Review the expected target shape and schedule one owning pipeline for that table.

## 4. Generate, validate and open a PR

The agent uses the bundled example to scaffold `fabric/bronze_to_silver.Notebook/notebook-content.py` and its `.platform` descriptor. Fabric Git stores the PySpark source with cell and kernel metadata. The FabricOps release also ships `02_pipeline.ipynb` for notebook import. [Microsoft Fabric notebook source control](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-source-control-deployment).

Run the validator in your project's Python environment using the aliases confirmed in `00_env_config`.

```sh
python .agents/skills/fabricops-pipeline-builder/scripts/validate.py \
  fabric/bronze_to_silver.Notebook --store Bronze --store Silver --fabricops-version 0.5.0
```

Local validation checks the version and callable signatures, Git artifact layout and lifecycle, required operation settings, and overlaps detectable from declared coordinates. Fabric must confirm installed libraries, physical bindings, permissions, query and transformation behavior, and Data Contracts. Review aliases that could point to the same physical location and verify that the transformation retains every required column. The generated notebook is ready for code review once these local checks pass and remaining Fabric prerequisites are recorded.

Open a PR in the consumer repository. Include the source, target, transformation, keys, Read and Write strategies, execution mode, validation command and outcome, and pending Fabric steps. Ask the project owner to review the notebook before merging.

## 5. Merge, sync and run in Fabric

1. Merge through the consumer's usual review process, then update the connected development workspace from Git in Fabric.
2. Attach the project's published Fabric Environment. Confirm that the workspace can run its configured `00_env_config` and resolve the stores, that metadata has been initialized by Governance, and that the run identity has the required access. [Configure the Environment and load assets](guided-demo/00B-configure-environment-and-load-assets.md).
3. Run the saved notebook end to end in **Dry Run** in development. Check the deduplicated data, prepared target input and Finalize result. Dry Run reads real data and previews the Write without publishing business rows. FabricOps can save the completed candidate for review.
4. For a governed deployment, follow the existing Data Contract Activation and Pipeline Approval workflow and deploy the approved snapshot through Pipeline Promotion. A PR merge or Git sync leaves those steps to the authorized owners. Governed admission in v0.5.0 remains fail closed pending signed-in Fabric acceptance. [Activate contracts and deploy](guided-demo/05-activate-contracts-and-deploy.md).
