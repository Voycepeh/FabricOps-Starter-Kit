# Source package guide (`src/fabricops_kit`)

This package keeps runtime logic in `src/fabricops_kit/` and publishes user-facing callables through `fabricops_kit.__all__` in `src/fabricops_kit/__init__.py`.

## Public callable catalogue sources

- **Public callable source of truth:** `__all__` in `src/fabricops_kit/__init__.py`.
- **Generated docs outputs:**
  - Step-first reference: `docs/reference/index.md`
  - Module catalogues: `docs/api/modules/*.md`

## Regenerate the function reference

```bash
PYTHONPATH=src python scripts/generate_function_reference.py
```

Run the generator whenever public exports change (add/remove/rename) so GitHub Pages stays aligned with the package surface.
