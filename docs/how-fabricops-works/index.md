# How FabricOps Works

FabricOps Starter Kit is a lightweight Microsoft Fabric notebook starter kit.

We adopt a Fabric notebook-first approach for data exploration, data pipelines, and governance.

It helps governance teams, analysts, and engineers work from a shared structure without adding a large platform around Fabric.

These notebooks capture agreements, profiling results, quality rules, classifications, lineage, drift checks, and production evidence. 
The evidence is stored in a metadata lakehouse and presented through a Power BI dashboard.

**The result is a self-contained Fabric workflow for governing data products without adding a separate platform.**
- Configure the environment so every notebook writes to the right workspace, lakehouse, warehouse, and metadata target.
- Capture the agreement so ownership, approved usage, and stewardship are recorded before delivery.
- Explore and build with notebooks so profiling, transformation, lineage, drift, and quality evidence are created as part of the work.
- Review governance centrally so business context, rules, classifications, and exceptions are approved in one place.
- Run approved notebooks in production so production outputs are created from production config and approved metadata.
- Present the evidence in Power BI so users can see coverage, health, lineage, and readiness without reading raw metadata tables.

## Workspace setup

<figure markdown>
  ![FabricOps Starter Kit operating model with Governance, Engineering Dev, and Engineering Prod workspaces](../assets/fabricops-operating-model-overview.png){ .full-width }
  <figcaption>Governance, Engineering Dev, and Engineering Prod workspaces separate shared metadata from development and production processing.</figcaption>
</figure>

The workspace operating model explains how the Governance, Engineering Dev, and Engineering Prod workspaces work together, including production promotion and storing final notebook evidence.

[Open Workspace Operating Model](workspace-operating-model.md){ .md-button .md-button--primary }

## Notebook workflow

<figure markdown>
  ![Role-based notebook workflow from environment configuration through AI-assisted handover](../assets/fabricops-role-workflow.png){ .full-width }
  <figcaption>The notebook flow connects configuration, agreements, exploration, pipeline delivery, governance enrichment, enforcement, and production handover evidence.</figcaption>
</figure>

The notebook templates page explains what each notebook owns, who uses it, and how the notebook flow passes reusable evidence from one role to the next.

[Open Notebook Templates](notebook-templates.md){ .md-button .md-button--primary }

## Metadata architecture

<figure markdown>
  ![Shared FabricOps metadata model connecting governance and engineering notebooks](../assets/fabricops-metadata-model.png){ .full-width }
  <figcaption>The governance metadata lakehouse acts as the shared coordination layer between governance and engineering.</figcaption>
</figure>

The metadata tables page explains how the notebooks store reusable evidence for agreements, profiles, quality rules, governance review, lineage, drift, and notebook registration.

[Open Metadata Tables](metadata-tables.md){ .md-button .md-button--primary }

## Metadata dashboard

<figure markdown>
  ![FabricOps metadata dashboard wireframe](../assets/fabricops-metadata-dashboard.png){ .full-width }
  <figcaption>The metadata dashboard turns collected metadata into a user-facing Power BI reporting layer.</figcaption>
</figure>

The metadata dashboard page explains the recommended dashboard wireframe and the assembled views consumed by the dashboard.

[Open Metadata Dashboard](metadata-dashboard.md){ .md-button .md-button--primary }
