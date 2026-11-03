"""Retained Run format integrity after additive activation provenance columns."""
from datetime import datetime
from copy import deepcopy
import pytest
from fabricops_kit.pipeline import shared
from fabricops_kit.activated_pipeline.shared import manifest_digest, RUN_PROVENANCE_FIELDS


def legacy_run():
    """Return an original hash-bearing Run without newer physical provenance."""
    return dict(run_id="retained", pipeline_id="logical", execution_mode="testing", workspace_id="DEV",
        started_at=datetime(2026, 1, 1), completed_at=None, status="incomplete", boundary_completed=False,
        approval_id=None, activation_revision=None, operations=[], profiling=[], failures=[], warnings_json="[]")


def test_null_additive_columns_preserve_exact_historical_hash():
    """Spark's additive nulls cannot alter a frozen Test's original evidence."""
    original = legacy_run()
    digest = manifest_digest(original)
    padded = {**deepcopy(original), **dict.fromkeys(RUN_PROVENANCE_FIELDS)}
    assert shared.validate_pipeline_run(padded) == original
    assert manifest_digest(shared.validate_pipeline_run(padded)) == digest
    # Literal golden protects the exact historic hash format.
    assert digest == '0e731725fb75fd4ab578903d7e14802d47068c065289c98e241d2c1213ce47f6'


@pytest.mark.parametrize("field", RUN_PROVENANCE_FIELDS[:-1])
def test_unversioned_run_rejects_nonnull_new_provenance(field):
    """Unexpected new facts on old evidence fail rather than being erased for a hash."""
    with pytest.raises(ValueError, match="unexpected new provenance"):
        shared.validate_pipeline_run({**legacy_run(), field: "forged"})


def test_unknown_run_version_rejected():
    """A newer evidence version cannot accidentally use the old hash semantics."""
    with pytest.raises(ValueError, match="schema version"):
        shared.validate_pipeline_run({**legacy_run(), "run_schema_version": 99})
