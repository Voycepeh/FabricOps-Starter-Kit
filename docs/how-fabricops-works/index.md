# How FabricOps Works

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit.

It helps governance teams, analysts, data scientists, and engineers work from a shared structure without adding a large platform around Fabric.

The simple idea is:

- **Governance owns shared metadata.**
- **Engineering owns exploration, transformation, and product outputs.**
- **Notebook templates connect the roles.**
- **Metadata tables store evidence.**
- **Assembled views and dashboards make the metadata useful.**
- **Production handover is generated from approved metadata and exported notebook evidence.**

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

1. [Workspace and Notebook Flow](workspace-and-notebook-flow.md): configure the three workspaces and run the templates in sequence.
2. [Metadata Tables](metadata-tables.md): understand the evidence captured by the notebooks.
3. [Assembled Views and Dashboards](assembled-views-and-dashboards.md): turn raw metadata into useful views for people and tools.
4. [Production and Handover](production-and-handover.md): promote the production notebook and generate reusable support material.
