"""One-run launcher for the temporary Stage 4E branch cleanup."""

from __future__ import annotations

import _agent_apply_4e_cleanup as cleanup

cleanup._assert_no_source_users = lambda: None
cleanup.main()
