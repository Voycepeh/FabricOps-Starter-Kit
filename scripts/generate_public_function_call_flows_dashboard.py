"""Generate the v4 public-function call-flow dashboard."""

try:
    from scripts.public_function_call_flows_dashboard_renderer import *  # noqa: F403
    from scripts.public_function_call_flows_dashboard_renderer import main
except (ImportError, ModuleNotFoundError):  # Direct ``python scripts/...`` execution.
    from public_function_call_flows_dashboard_renderer import *  # noqa: F403
    from public_function_call_flows_dashboard_renderer import main


if __name__ == "__main__":
    main()
