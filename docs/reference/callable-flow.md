# Callable Functions Flow

This page embeds the interactive callable functions dashboard.

Use the dashboard to inspect public API entrypoints, internal helpers, utilities, unreachable callables, caller/callee relationships, helper depth, reuse, and refactor review recommendations.

FabricOps callables are organized into three dependency layers: public API callables, internal helpers, and utilities. Public callables form the supported user-facing API and may depend on internal helpers or utilities. Internal helpers may depend only on utilities. Utilities should be leaf callables and should not depend on other project callables. Same-layer calls and upward calls between classified callables are flagged as architecture violations; calls to classification-pending or unreachable callees are review signals instead of layer violations.

[Open full dashboard](../assets/callable-functions-dashboard.html){ .md-button .md-button--primary }

<iframe
  src="../../assets/callable-functions-dashboard.html"
  title="Callable functions dashboard"
  width="100%"
  height="900"
  loading="lazy"
  style="border: 1px solid var(--md-default-fg-color--lightest); border-radius: 0.5rem;">
</iframe>

If the embedded view is too small, open the full dashboard directly.

The dashboard data comes from [`_data/callable-flow.json`](_data/callable-flow.json).