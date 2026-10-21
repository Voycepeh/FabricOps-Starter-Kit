---
name: fabricops-widget-ui
description: Design, polish, and visually verify FabricOps ipywidgets, including form alignment, responsive layouts, and expanded states.
---

# FabricOps Widget UI

Read [Frontend Design](../frontend-design/SKILL.md) first. Apply its design planning and screenshot critique to the existing Microsoft Fabric notebook product. Follow `AGENTS.md` and use [Public API Change](../fabricops-public-api-change/SKILL.md) for callable source changes.

## Brief and design direction

The audience is data engineers and governance authors completing governed notebook workflows. Prioritize task clarity, stable form geometry, and readable data over decorative novelty. Keep native ipywidgets and Fabric-native DataFrame display. Do not replace the runtime with a web framework or require external fonts or assets.

Before editing, inventory exported widgets and embedded notebook widget flows. Inspect shared composers, owner layouts, and relevant tests. Write a compact design plan covering tokens, typography, alignment, and expansion behavior. Critique it against the actual workflows before coding.

Use a restrained Fabric-inspired palette:

| Token | Value | Purpose |
| --- | --- | --- |
| Canvas | `#f6f8fb` | Quiet notebook form background |
| Surface | `#ffffff` | Editable sections |
| Text | `#243449` | Headings, labels, values |
| Border | `#dce4ed` | Meaningful section and input boundaries |
| Engineering | `#0f6cbd` / `#eaf3fb` | Blue accent / pastel header |
| Governance | `#6750a4` / `#f1edf8` | Purple accent / pastel header |

Use governance styling for Data Contract authoring, activation, Data Agreement, and Data Steward. Use engineering styling for the Catalogue viewer and pipeline setup. Preserve text titles so color is never the only distinction. Treat this as a product palette, not a claim of official Microsoft design tokens.

Use Segoe UI with system fallbacks for a native Fabric feel. Use sentence case, a small type scale (21px page title, 14–15px section heading, 13px controls), and visible keyboard focus. Use status colors only for actual status or action meaning. Favor clear borders over shadows and nested decorative cards.

## Form geometry

- Put labels above full-width controls. Keep controls and section headings on common left edges.
- Use a consistent input height, border, radius, and section padding. Textareas and multi-selects need enough height for their content plus labels.
- Keep checkbox captions next to their checkbox, left aligned; hide only their unused description spacer. Group related toggles explicitly.
- Keep amounts and units in equal, adjacent cells beneath one label. Keep parameter options grouped below the field they modify.
- Use shared composers and shared CSS for common behavior. Keep owner CSS limited to workflow-specific layout. Remove competing global layout CSS rather than accumulating overrides.
- Use `Layout.grid_gap` for GridBox and actual CSS classes for flex gaps; do not rely on unsupported `Layout(gap=...)` arguments.
- Give HTML widgets their own block layout. Never apply the input grid to headers, HTML summaries, or tables.
- Let narrow notebook containers stack panels based on container width. Avoid fixed minimum widths that force horizontal overflow.

## Calls to action

Use a solid workflow accent for the main action in each task area: Generate, Add/Update, Save, or final activation. Use outlined accent buttons for alternate or preparatory actions such as opening with AI or initiating freeze. Keep cancel, refresh, and navigation neutral. Use outlined red for destructive requests and solid red only for the final destructive confirmation. Green communicates success status rather than generic action emphasis. Disabled actions need legible neutral styling, not faded saturated fills.

## Expansion and interaction

- Expanding controls must not change the width or position of neighboring panels. Keep disclosure titles stable; expose state with the toggle, chevron, and tooltip.
- Contain long navigation in a bounded sidebar with a stable scrollbar gutter. Keep main form sections in the shared notebook viewport.
- Let expanded details wrap naturally inside their region. Tables and JSON must remain reachable without stretching the overall page.
- Keep AI authoring and review panes at matching heights, with scrollable bodies and anchored action footers. Long results, errors, and Engineering review fields must stay inside those bodies. Use one active reviewer that switches between generated proposals and current draft rules instead of stacking both flows.
- Show a busy state during generation, prevent duplicate generation clicks, and restore the CTA after success or failure. Review generated results before adding them to the draft.
- Preserve unsaved edits, selected values, disabled states, confirmation flows, save behavior, and all persisted data contracts.
- Preserve the notebook scroll safeguard while retaining normal keyboard operation and visible focus.

## Verification and critique

Render the actual widget controls with generic, in-memory service fixtures when Fabric is unavailable. Mock I/O services, not widget rendering. Do not write preview data to Fabric. Review every exported widget and embedded pipeline setup flow, not only the landing state.

Capture and inspect screenshots at wide, medium, and narrow notebook widths. Exercise populated and empty views, alternate tabs, conditional fields, disclosures, repeated rows, and confirmation states where relevant. Confirm controls fit their cells, labels do not overlap, sections share edges, and expansion does not move adjacent panels. Check mouse and keyboard interaction.

Run focused widget tests, lint, and syntax checks. Update assertions for intentional layout changes while preserving behavioral coverage. Follow repository rules for generated source references and call-flow data. Report what was previewed, what was verified with tests, and any Fabric-only limitations. Keep screenshots outside package source unless specifically requested as documentation assets.
