# 0A. Prepare the Fabric environment

**Create the Fabric workspaces, data stores, and Fabric Environment required by the Guided Demo.**

This is foundation setup, not one of the seven lifecycle steps.

## 1. Open Microsoft Fabric

Go to [Microsoft Fabric](https://app.fabric.microsoft.com/) and sign in with your Microsoft account.

If you do not already have Fabric capacity available, start a Fabric trial so you can create and run the items used in this demo.

## 2. Create the workspaces

Create the following workspaces:

| Workspace | Required now? | Used for |
| --- | --- | --- |
| **Governance** | Yes | Governance metadata, Data Stewards, Data Agreements, and Data Contracts. |
| **Engineering Development** | Yes | Building and validating the pipeline. |
| **Engineering Production** | Optional for now | Step 6 of the seven-step workflow. |
| **Consumer** | Optional for now | Step 7 of the seven-step workflow. |

You only need **Governance** and **Engineering Development** to begin the walkthrough. You can create the Production and Consumer workspaces later when you reach those steps.

![Fabric workspace creation](../assets/00A/Workspace.png)

## 3. Create the Fabric data stores

### Governance workspace

Open the **Governance** workspace and create a Lakehouse named:

```text
metadata
```

This Lakehouse stores the FabricOps Governance metadata used throughout the demo.

![Create the metadata Lakehouse](../assets/00A/Create_Lakehouse.png)

### Engineering Development workspace

Open the **Engineering Development** workspace and create:

1. a Lakehouse named `bronze`
2. a Lakehouse named `silver`
3. a Warehouse named `gold`

These give the demo a simple medallion-style Engineering layout while still allowing FabricOps to route reads and writes through logical stores configured later in `00_env_config`.

![Engineering Development Fabric items](../assets/00A/Objects.png)

### Engineering Production workspace

When you are ready for Step 6, repeat the Engineering Development setup in **Engineering Production**. Production should be a **1:1 mirror** of the Development workspace structure:

- `bronze` Lakehouse
- `silver` Lakehouse
- `gold` Warehouse

The **Consumer** workspace does not need its own Fabric data store for this Guided Demo. It will consume the approved Production output in Step 7.

## 4. Get FabricOps

Use the latest FabricOps release from the [FabricOps Starter Kit Releases page](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases).

The easiest option is to download the `.whl` file attached to the release you want to use.

If you prefer to build FabricOps yourself, clone the repository locally and run:

```bash
uv build
```

The built wheel will be created under `dist/`.

## 5. Create the Fabric Environment

Return to the **Governance** workspace and create a Fabric **Environment** for FabricOps.

Open the Environment, go to **Custom libraries**, upload the FabricOps `.whl` file, then **Publish** the Environment.

Publishing makes the installed FabricOps package available when the Environment is attached to the notebooks used later in the Guided Demo.

![Install the FabricOps wheel as a custom library](../assets/00A/install-custom-whl.png)

## Expected result

You now have:

- the Governance and Engineering Development workspaces required to start the demo
- optional Production and Consumer workspaces ready for Steps 6 and 7 if you created them
- the Governance `metadata` Lakehouse
- Engineering `bronze`, `silver`, and `gold` stores
- a published Fabric Environment containing the FabricOps wheel

**Next:** [0B. Configure the environment and load demo data](00B-run-environment-setup.md)
