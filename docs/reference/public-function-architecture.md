# Public Function Architecture

FabricOps uses a strict public/shared/init package pattern for every new public callable function.

## Rule

For every new public callable function added to FabricOps:

1. Create or use a package folder for the functional batch.
2. Put each public callable function in its own owner file named exactly after the function.
3. Put shared helpers, private helpers, support classes, dataclasses, and value objects for that batch in `shared.py`.
4. Re-export the supported public surface through that package's `__init__.py`.
5. Re-export notebook-facing public functions/classes through `src/fabricops_kit/__init__.py` only when they are part of the supported root API.
6. Do not add `public.py`, `models.py`, `classes.py`, `adapter.py`, `adapters.py`, `resolver.py`, `resolvers.py`, or compatibility shim files unless explicitly approved.

## Standard package shape

For one public function:

```text
src/fabricops_kit/my_feature/
  __init__.py
  my_public_function.py
  shared.py
```

For multiple public functions in the same batch:

```text
src/fabricops_kit/my_feature/
  __init__.py
  first_public_function.py
  second_public_function.py
  shared.py
```

For public classes or config objects used by the batch:

```text
src/fabricops_kit/my_feature/shared.py
  MyConfig
  MyResult
  _private_helper
  shared_core_logic
```

## Public owner files

Each public owner file should contain the public callable with the same name as the file.

Example:

```python
# src/fabricops_kit/my_feature/my_public_function.py

from .shared import _my_public_function_workflow


def my_public_function(...):
    return _my_public_function_workflow(...)
```

The file should not define extra public functions or classes.

## shared.py

`shared.py` owns everything that supports the public callables in the package:

- private helpers
- shared core workflows
- dataclasses
- value objects
- support classes
- constants used across the batch

Use private names for helpers that are not part of the public API.

## __init__.py

`__init__.py` is the package export surface.

Example:

```python
from .my_public_function import my_public_function
from .shared import MyConfig, MyResult

__all__ = [
    "my_public_function",
    "MyConfig",
    "MyResult",
]
```

## Root package exports

Only expose names from `src/fabricops_kit/__init__.py` when they are supported for notebook authors or templates.

Templates should import from the root package:

```python
from fabricops_kit import my_public_function
```

Templates should not import from internal package paths.

## Classes in the reference

Public classes should be exposed under a Classes category in reference docs and dashboards.

They should not be counted as public callable functions.

Use these counts separately where possible:

- public callable functions
- public classes
- public root exports total

## Forbidden files

Do not create these files inside package-batch directories unless explicitly approved:

- `public.py`
- `models.py`
- `classes.py`
- `adapter.py`
- `adapters.py`
- `resolver.py`
- `resolvers.py`

The preferred structure is always:

- one owner file per public function
- one `shared.py`
- one `__init__.py`

## Enforcement

The test suite enforces this pattern.

It checks that:

1. package directories do not introduce forbidden grouping files
2. every public owner file defines at most one public function
3. the public function name matches the file name
4. public owner files do not define classes
5. batch classes and dataclasses live in `shared.py`
6. `__init__.py` is the supported package export surface

## Why this pattern exists

This keeps FabricOps easy to explain and maintain:

- users see a clean root import surface
- every public function has an obvious source file
- shared implementation details stay behind the scenes
- reference docs can map functions/classes cleanly
- new features do not grow into catch-all modules
