test:
    uv run pytest tests

test-py version:
    uv run --python {{version}} pytest tests

test-all:
    uv run --python 3.11 pytest tests
    uv run --python 3.12 pytest tests
