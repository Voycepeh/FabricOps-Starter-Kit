# How FabricOps Works

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit.

It helps governance teams, analysts, and engineers work from a shared structure without adding a large platform around Fabric.

The simple idea is:

- **Governance owns shared metadata.**
- **Engineering owns exploration, transformation, and product outputs.**
- **Notebook templates connect the roles.**
- **Metadata tables store evidence.**
- **The metadata dashboard makes the metadata useful.**
- **Production handover evidence comes from the approved production notebook.**

## Workspace setup

<figure markdown>
  ![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png){ .full-width }
  <figcaption>One config notebook, role-based templates, and shared metadata connect the recommended Fabric workspaces.</figcaption>
</figure>

## Role-based notebook workflow

<figure markdown>
  ![Role-based notebook workflow from environment configuration through AI-assisted handover](../assets/fabricops-role-workflow.png){ .full-width }
  <figcaption>The notebook flow connects configuration, agreements, exploration, pipeline delivery, governance enrichment, enforcement, and handover.</figcaption>
</figure>

## In built metadata data architecture

<figure markdown>
  ![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }
  <figcaption>The governance metadata lakehouse is the shared coordination layer between governance and engineering.</figcaption>
</figure>

## Read More

1. [Workspace Operating Model](workspace-operating-model.md): understand the three workspaces, production promotion, and handover evidence.
2. [Notebook Templates](notebook-templates.md): run the Fabric notebook templates in sequence.
3. [Metadata Tables](metadata-tables.md): understand the evidence captured by the notebooks.
4. [Metadata Dashboard](metadata-dashboard.md): turn governed metadata into dashboard-ready reporting views.
