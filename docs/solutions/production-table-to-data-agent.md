# Production Table to Data Agent

<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>

![Production Table to Data Agent](../assets/DataAgentsBootstrap.png){ .fabricops-solution-hero }

## The problem

Microsoft Fabric Data Agents can already work well out of the box, particularly with a single, well-structured table.

The harder cases are the business semantics that the data alone cannot reliably resolve. A table might contain `order_date`, `ship_date`, and `payment_date`; `gross_amount` and `net_amount`; or several similar customer identifiers. Every column may be valid, but choosing the wrong one can produce a technically correct query that answers the wrong business question.

To configure a Data Agent well, teams usually need to provide this business context manually. But by the time a table has gone through the previous six FabricOps lifecycle steps, much of that work has already been done: its purpose, grain, column meaning, business rules, sensitivity, limitations, and other governed context have already been captured.

That creates a natural opportunity: **reuse the context FabricOps already has to bootstrap a better-configured Data Agent instead of asking the team to describe the Production table again.**

## The solution

FabricOps reuses the governed context it already has: table purpose, grain, business terminology, column descriptions, approved business rules, known limitations, classification, sensitivity, and other Data Contract context.

FabricOps prepares the governed context of the Production table into Data Agent instructions, then uses the Microsoft Fabric API to create and configure the Data Agent with those instructions.

This means that at **Step 7, the final stage of the FabricOps lifecycle**, the governed Production table can be handed off as a ready-to-use Data Agent for consumption, reusing the context captured throughout the previous six steps.

**Governed Production Table + FabricOps Context → Data Agent Instructions → Fabric API → Data Agent ready for consumption**

The Data Agent still queries the **actual Production data** through Microsoft Fabric. FabricOps does not copy business-table rows into the prompt or replace Fabric permissions. It supplies business context that cannot always be inferred safely from the data alone.

**Current Preview scope:** FabricOps currently provides `create_data_agent()`, which creates and configures a Data Agent from **one governed Production table**. Multi-table support is planned for a future iteration.

## How it works

| Responsibility | What happens |
| --- | --- |
| **Human governs** | Captures the table purpose, grain, business terminology, column descriptions, approved business rules, known limitations, classification, and sensitivity during the normal FabricOps lifecycle. |
| **Data Agent uses** | Uses the supplied governed instructions when interpreting consumer questions and queries the actual Production table through Microsoft Fabric. When meaning is still ambiguous, the instructions tell the agent to ask rather than guess. |
| **FabricOps handles deterministically** | Resolves the activated Production Data Contract and catalogue identity, selects consumer-useful governed context, renders agent and datasource instructions, creates the native Fabric Data Agent through the Fabric REST API, and attaches the governed Production table as its datasource. |

Fabric permissions remain authoritative for access to the Production data and for creating the Data Agent.

## Under the hood

<details class="fabricops-solution-details" markdown="1">
<summary><strong>How FabricOps prepares and applies the Data Agent instructions</strong></summary>

![FabricOps Production table to Data Agent implementation](../assets/data-agent-bootstrap-implementation.svg){ .fabricops-solution-diagram }

`create_data_agent()` uses the current Fabric notebook caller identity to call the Microsoft Fabric REST API. It creates the Data Agent, attaches the configured Production Lakehouse or Warehouse datasource, selects the governed table, and applies the generated datasource and agent instructions.

FabricOps does **not** copy the Production table into an AI prompt. The table remains a Fabric datasource and the caller's Fabric permissions continue to control access.

</details>

## Example

<details class="fabricops-solution-details" markdown="1">
<summary><strong>Example Data Agent instructions</strong></summary>

For a governed Orders table, FabricOps can prepare instructions such as:

**Table context**

- Purpose: Governed Production order records.
- Grain: One row per order.
- `order_date`: Date the order was placed.
- `ship_date`: Date the order was shipped.
- `payment_date`: Date payment was received.
- `gross_amount`: Amount before deductions.
- `net_amount`: Amount after deductions.

**Data Agent instructions**

- Use the governed table and column descriptions when interpreting business questions.
- Do not invent business meaning that is not provided in the governed context.
- Treat `order_date`, `ship_date`, and `payment_date` as distinct business concepts.
- Treat `gross_amount` and `net_amount` as distinct measures.
- When a question could reasonably refer to multiple governed concepts, ask the user to clarify before choosing one.
- For example, if a user asks for "monthly orders", clarify which governed date concept they intend when the question does not make that clear.

The exact instructions are generated from the governed context available for the selected Production table rather than maintained as a separate manual description of the same table.

</details>

## Go deeper

Use [Step 7: Governed Consumption](../guided-demo/07-consume-production-data.md) to see where the Data Agent handoff fits in the governed consumer lifecycle.

Use the generated [`create_data_agent()` reference](../api/reference/create_data_agent.md) for the exact Preview API contract, prerequisites, parameters, errors, and implementation details.
