"""Generate release contract documentation pages and release navigation."""

from release_inventory import pages_main
from release_navigation import sync_release_navigation


if __name__ == "__main__":
    result = pages_main()
    sync_release_navigation()
    raise SystemExit(result)
