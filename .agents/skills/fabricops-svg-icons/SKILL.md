---
name: fabricops-svg-icons
description: Use when creating, sourcing, modifying, or reviewing an SVG icon or an explicitly requested FabricOps logo.
---

# FabricOps SVG Icons

## External skill to consult

Before creating or editing an icon or an explicitly requested logo, inspect the upstream [SVG Icon Generator skill](https://awesomeskill.ai/skill/claude-code-plugins-plus-skills-svg-icon-generator), originally attributed to [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills). Prefer the source `SKILL.md` when still available. The upstream repository may move or redirect; verify the actual source before blindly downloading/installing anything.

The published skill is general **SVG creation/validation guidance**, not a rendering engine, guaranteed high-quality logo designer, or required executable dependency. Apply its best practices and our concrete standards below; do not claim that merely referencing it generates assets.

For architecture and workflow diagrams, additionally use `.agents/skills/fabricops-visual-design/SKILL.md` and the [Diagram Design skill](https://github.com/cathrynlavery/diagram-design). The icon skill owns icon geometry and reuse; the diagram skill owns layout, arrows, visual hierarchy and semantics.

## Icon library

1. Prefer existing approved icons and reuse them consistently; create a new icon only when no existing semantic icon fits.
2. Icons should use a consistent **24 × 24 viewBox**, 1.75px default stroke, round line caps/joins, no exaggerated effects. Stay readable at 16px, 24px and 48px.
3. Use `currentColor` for reusable UI icons so the owning component controls the semantic colour. For standalone static diagrams, a single neutral ink stroke is the default. Blue indicates Engineering emphasis, purple only an actual Governance owner/gate/handoff, green success, amber warning, red error. Do not colour ordinary steps individually.
4. Each icon must have one clear meaning. Do not treat database, notebook, gear, shield, or cube pictograms as an official FabricOps brand symbol. An icon is not a logo.
5. No external URLs, embedded rasters, scripts, `foreignObject`, external fonts, inaccessible-only colour distinctions, or unlicensed provider marks. Keep the shape editable and standalone.
6. Prefer a neutral icon only when it clarifies meaning. If text is sufficient, omit the icon.
7. Use `aria-hidden="true"` when paired with a visible label, or `role="img"` and `<title>` when the icon itself conveys a label. Ensure contrast in all actual usage contexts.
8. Explicitly mark a generated logo as a **proposal** until approved. Do not insert it into site navigation, README or diagrams without user approval. Avoid resembling Microsoft/Fabric identity or implying affiliation.
9. Check the asset at 16/24/48px in both light and dark surfaces, check stroke and path clipping, and run SVG lint/render checks. Never substitute a PNG inside an SVG wrapper to claim editability.

## Workflow and outputs

Identify the meaning and destination, choose an existing asset or construct the SVG, render it, inspect the three sizes, validate its accessibility and security, and then add it to the relevant asset folder. Treat the repository's `design/brand.json` as canonical colour/type guidance.

Do not commit a full third-party skill repository or run its install scripts automatically. Reference the external skill for design patterns, and maintain only this repository-specific wrapper and original in-house assets.
