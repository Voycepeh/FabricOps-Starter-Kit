# 0A. Prepare the Fabric environment

**Create the Fabric workspaces and stores, then install FabricOps into a Fabric Environment.**

This is foundation setup, not one of the seven FabricOps lifecycle steps.

## 1. Open Microsoft Fabric

Open [Microsoft Fabric](https://app.fabric.microsoft.com/) and sign in with your Microsoft account.

You need access to Microsoft Fabric capacity to complete the walkthrough. If you do not already have access through your organisation, you can use a Fabric trial where available.

## 2. Create the workspaces

Create these workspaces for the walkthrough:

| Workspace | Required? | Used for |
| --- | --- | --- |
| **Governance** | Yes | Governance metadata, Data Stewards, Data Agreements, and Data Contracts. |
| **Engineering Development** | Yes | Build and validate the Engineering pipeline. |
| **Engineering Production** | Optional until Step 6 | Production mirror of the Development engineering workspace. |
| **Consumer** | Optional until Step 7 | Consume approved Production data. |

For Steps 1–5, only **Governance** and **Engineering Development** are required. Create the optional workspaces now if you want to follow the entire seven-step walkthrough without stopping later.

![Fabric workspaces for the Guided Demo](../assets/00A/Workspace.png)

## 3. Create the Governance metadata Lakehouse

Open the **Governance** workspace and create a Lakehouse named:

```text
metadata
```

FabricOps uses this Lakehouse to persist its Governance metadata throughout the walkthrough.

![Create the Governance metadata Lakehouse](../assets/00A/Create_Lakehouse.png)

## 4. Create the Engineering stores

Open **Engineering Development** and create:

| Item | Name | Role in the walkthrough |
| --- | --- | --- |
| Lakehouse | `bronze` | Source / landing data. |
| Lakehouse | `silver` | Curated engineering data. |
| Warehouse | `gold` | Product / serving data. |

![Engineering Development Fabric items](../assets/00A/Objects.png)

If you created **Engineering Production**, repeat the same setup there. Production should be a **1:1 structural mirror of Engineering Development**: `bronze`, `silver`, and `gold` with the same item types and names.

The **Consumer** workspace does not need its own Fabric store for this Guided Demo. It will consume approved Production data in Step 7.

## 5. Get FabricOps

The easiest option is to download the packaged FabricOps wheel from the [FabricOps Releases page](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases).

Download the `.whl` file from the release you want to run.

If you prefer to build FabricOps yourself, clone the repository locally and run:

```bash
uv build
```

The built wheel will be available under `dist/`.

## 6. Create a Fabric Environment and install FabricOps

Return to the **Governance** workspace and create a Fabric **Environment**.

In the Environment:

1. Open **Custom libraries**.
2. Upload the FabricOps `.whl` file.
3. Confirm the wheel appears in the custom library list.
4. **Publish** the Environment.

Publishing is required before the installed FabricOps package is available to notebooks that use this Environment.

![Install the FabricOps wheel as a custom library](../assets/00A/install-custom-whl.png)

## Expected result

You now have:

- a Governance workspace with the `metadata` Lakehouse and a published Fabric Environment containing FabricOps;
- an Engineering Development workspace with `bronze`, `silver`, and `gold`;
- optionally, a matching Engineering Production workspace for Step 6; and
- optionally, a Consumer workspace for Step 7.

The physical Fabric foundation is ready. The next step configures FabricOps to use these items and loads the demo data.

**Next:** [0B. Configure the environment and load demo data](00B-run-environment-setup.md)
