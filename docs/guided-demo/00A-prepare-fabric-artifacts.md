# 0A. Prepare the Fabric environment

### Before you begin

You need access to Microsoft Fabric to complete this walkthrough.

### Open Microsoft Fabric

Open [Microsoft Fabric](https://app.fabric.microsoft.com/) and sign in with your Microsoft account.

If your organisation does not provide Fabric capacity, you can use a Fabric trial where available.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-pointing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create the workspaces

Only **Governance** and **Engineering Development** are needed initially. You can add the Production and Consumer workspaces when you reach Steps 6 and 7.

</div>
</div>


![Fabric workspaces for the Guided Demo](../assets/00A/Workspace.png)


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-writing.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create the Governance metadata Lakehouse

Inside the **Governance** workspace and create a Lakehouse named **Metadata**, it is the shared home for FabricOps Governance records

</div>
</div>




Use this exact name and casing for the Guided Demo. FabricOps uses this Lakehouse to persist its Governance metadata throughout the walkthrough.



![Create the Governance metadata Lakehouse](../assets/00A/Create_Lakehouse.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create the Engineering stores

Open **Engineering Development** and create three distinct stores: **bronze**, **silver** lakehouse and **gold** warehouse.

</div>
</div>






![Engineering Development Fabric items](../assets/00A/Objects.png)

??? info "Optional: prepare Engineering Production and Consumer"


Production should be a **1:1 structural mirror** of Development so the validated pipeline can use the same logical stores after promotion.


    If you created **Engineering Production**, repeat the same setup there with `bronze`, `silver`, and `gold` using the same item types and names.

    The **Consumer** workspace does not need its own Fabric store for this Guided Demo.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Get FabricOps

Download the packaged FabricOps wheel from the [FabricOps Releases page](https://github.com/Voycepeh/FabricOps-Starter-Kit/releases).

</div>
</div>




Download the `.whl` file from the release you want to use, please check that you do not download the release version than is earlier than what was declared on the demo files you want to run, else the demo may not run correctly.



If you prefer to build FabricOps yourself, clone the repository locally and run:

```bash
uv build
```

The built wheel will be available under `dist/`.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create Fabric Environments and install FabricOps

Fabric Environments are **workspace-specific**. Install and publish the same FabricOps wheel in each workspace that runs FabricOps notebooks.

</div>
</div>





A Fabric Environment belongs to a workspace. An Environment created in Governance is not automatically available in Engineering Development, Engineering Production, or Consumer.

Start in the **Governance** workspace and create a Fabric **Environment**. Then:

1. Open **Custom libraries**.
2. Upload the FabricOps `.whl` file.
3. Confirm the wheel appears in the custom library list.
4. **Publish** the Environment.

Publishing is required before the installed FabricOps package is available to notebooks that use this Environment.

![Install the FabricOps wheel as a custom library](../assets/00A/install-custom-whl.png)


Use the same FabricOps wheel version in each workspace so Governance, Development, Production, and Consumer are running the same package version during the Guided Demo.

??? info "Optional: enable Fabric AI Functions for AI-assisted Governance"

    FabricOps does not require AI to author or enforce Data Contracts. The AI-assisted authoring controls in Step 3 are optional.

    If you want to use them, ask your Fabric administrator to confirm **Users can use Copilot and other features powered by Azure OpenAI** is enabled for the relevant users or capacity. Fabric AI Functions also require a supported Fabric region, Fabric Runtime 1.3 or later, and an eligible paid capacity. Depending on the capacity region, your organisation might also need to allow cross-geo processing.

    See [AI Functions prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/ai-functions/overview) and [Copilot and Agent tenant settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-copilot).

    You will enable or disable the FabricOps authoring integration itself through `GOVERNANCE_CONFIG.ai_enrichment.enabled` in `00_env_config`.

### Expected result

You now have:

- a Governance workspace with the `Metadata` Lakehouse and a published Fabric Environment containing FabricOps;
- an Engineering Development workspace with `bronze`, `silver`, and `gold`, plus its own published Fabric Environment containing the same FabricOps wheel;
- optionally, a matching Engineering Production workspace for Step 6, with its own Environment when you are ready to use it; and
- optionally, a Consumer workspace for Step 7, with its own Environment when you are ready to run project-specific consumer notebooks.

The physical Fabric foundation is ready. The next step imports the FabricOps notebook templates and demo data.

**Next:** [0B. Configure the environment and load demo data](00B-configure-environment-and-load-assets.md)
