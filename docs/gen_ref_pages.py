"""MkDocs gen-files hook kept for compatibility.

Canonical callable reference pages are generated as committed files by
``scripts/generate_function_reference.py`` under ``docs/api/reference/``.
This hook intentionally does not write callable pages so MkDocs cannot create
a second virtual copy of the same public callable documentation.
"""
from __future__ import annotations

# Intentionally empty. See scripts/generate_function_reference.py.
