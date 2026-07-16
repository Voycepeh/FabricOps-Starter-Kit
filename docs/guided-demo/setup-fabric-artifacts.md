# Setup Fabric Artifacts

Create or choose the Microsoft Fabric runtime artifacts that the guided demo uses. Start with an already published FabricOps release wheel, then complete these steps before [Run Environment Setup](run-environment-setup.md).

## What you prepare

This page consolidates workspace, lakehouse, warehouse, Environment, published wheel upload, and notebook-copy setup into one practical Fabric-side sequence.

By the end, your copied notebooks can import `fabricops_kit`, and `00_env_config` can point every `METADATA_*` operation at the configured metadata lakehouse rather than an attached default lakehouse.

## 1. Create or choose a Fabric workspace

1. Open Microsoft Fabric.
2. Create a new demo workspace, or choose an existing safe workspace for public-safe testing.
3. Keep item names simple and recognizable so junior users can copy them into `00_env_config`.

For a lightweight demo, one workspace is enough. If your team separates governance and engineering workspaces, keep the item roles clear so the configured routes remain easy to understand.

## 2. Create or select lakehouses and warehouse

Create or select the Fabric data items that the demo will route through `00_env_config`.

| Item | Purpose |
| ---- | ------- |
| `metadata_lakehouse` | Stores the implemented steward, agreement, contract, catalogue, profile, lineage, access, enrichment, guardrail, and guardrail result tables. |
| `source_lakehouse` | Stores the public-safe files and source tables used during the Guided Demo. |
| `unified_lakehouse` | Stores governed outputs written by `02_pipeline`. |
| `product_warehouse` | Optional warehouse target for demos that need warehouse publishing. |

Record the workspace, lakehouse, warehouse, and schema names so you can enter them in `00_env_config` during [Run Environment Setup](run-environment-setup.md).

!!! note "Metadata target routing"
    Metadata reads and writes should use the configured `metadata_lakehouse` target from `00_env_config`. Do not rely on the attached or default lakehouse for `METADATA_*` tables.

## 3. Create or select a Fabric Environment

1. In the target Fabric workspace, create a new Fabric Environment or open the Environment that should run the guided demo notebooks.
2. Use one Environment for the copied demo notebooks so every notebook imports the same FabricOps package version.
3. Save or publish Environment changes when Fabric prompts you.

## 4. Upload and install the FabricOps wheel

Use the `.whl` file attached to the GitHub Release you want to demo. Repository maintainers build release wheels as part of the [Release Guide](../maintainer/index.md).

1. Open the FabricOps Starter Kit GitHub Release for the version you want to use.
2. Download the release wheel, for example `fabricops_kit-0.1.0-py3-none-any.whl`. The exact version number may differ.
3. Open the Fabric Environment.
4. Go to **Libraries** / **Custom libraries**.
5. Upload the downloaded wheel.
6. Save or publish the Environment so Fabric applies the library change.
7. Restart notebook sessions after changing the Environment if Fabric prompts you or if sessions were already running.

![Fabric custom wheel install example](../assets/fabric-example-install-custom-whl.png)

!!! tip "Use the wheel artifact"
    Upload the release `.whl`, not a `.zip`, the `.tar.gz` source distribution, `uv.lock`, or the repository folder.

## 5. Copy template notebooks

Download or copy editable notebook templates from the GitHub [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder into your Fabric workspace. Keep names recognizable for the first guided demo run.

| Notebook template | Role in the guided demo |
| ----------------- | ----------------------- |
| `00_env_config` | Defines shared environment, workspace, lakehouse, warehouse, metadata target, and audit settings. |
| `01_agreement` | Captures steward and agreement metadata. |
| `02_pipeline` | Runs governed source-to-target processing, profiles data, evaluates guardrails, writes outputs, and records catalogue, profile, lineage, and guardrail result evidence. |
| `03_governance` | Reviews observed metadata, enrichment intent, and guardrail intent. |
| `99_explore` | Supports optional read-only discovery or troubleshooting. |

![Fabric workspace setup example](../assets/fabric-example-workspace-setup.png)

## Expected result

The workspace contains editable copies of the guided demo notebooks, the Fabric Environment has the FabricOps wheel installed, and at least one copied notebook can import `fabricops_kit`.

No FabricOps metadata is required yet. This step prepares the runtime and workspace items that later pages use.

Next, continue to [Run Environment Setup](run-environment-setup.md).
