from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit import add_runtime_audit_columns, standardize_columns


def test_add_runtime_audit_columns_adds_only_lightweight_audit_columns():
    df = pd.DataFrame({"customer_id": [1001], "event_ts": ["2026-01-01T09:00:00Z"]})

    out = add_runtime_audit_columns(
        df,
        run_id="run-123",
        pipeline_name="customer_pipeline",
        environment="dev",
        source_table="minimal_source",
        notebook_name="03_pc_customer_pipeline",
        loaded_by="fabricops-test",
    )

    expected_audit_columns = [
        "_pipeline_run_id",
        "_pipeline_name",
        "_pipeline_environment",
        "_source_table",
        "_record_loaded_timestamp",
        "_notebook_name",
        "_loaded_by",
    ]
    assert list(out.columns) == ["customer_id", "event_ts", *expected_audit_columns]
    assert out.loc[0, "_pipeline_run_id"] == "run-123"
    assert out.loc[0, "_pipeline_name"] == "customer_pipeline"
    assert out.loc[0, "_pipeline_environment"] == "dev"
    assert out.loc[0, "_source_table"] == "minimal_source"
    assert out.loc[0, "_notebook_name"] == "03_pc_customer_pipeline"
    assert out.loc[0, "_loaded_by"] == "fabricops-test"


def test_add_runtime_audit_columns_does_not_add_specialized_columns_by_default():
    df = pd.DataFrame({"customer_id": [1001], "event_ts": ["2026-01-01T09:00:00Z"]})

    out = add_runtime_audit_columns(df, run_id="run-123", pipeline_name="pipeline", environment="dev", source_table="source")

    specialized_columns = {
        "_business_key_hash",
        "_row_hash",
        "_partition_bucket",
        "_sample_bucket",
        "_watermark_value",
        "_row_ingest_id",
        "EVENT_DTM_UTC8",
        "EVENT_DATE_UTC8",
        "EVENT_TIME_UTC8",
        "EVENT_HOUR_UTC8",
        "EVENT_TIME_BLOCK_30_MIN",
    }
    assert specialized_columns.isdisjoint(out.columns)


def test_standardize_columns_is_backward_compatible_audit_wrapper_only():
    df = pd.DataFrame({"customer_id": [1001], "event_ts": ["2026-01-01T09:00:00Z"]})

    with pytest.warns(DeprecationWarning, match="standardize_columns no longer adds"):
        out = standardize_columns(
            df,
            run_id="run-123",
            pipeline_name="pipeline",
            environment="dev",
            source_table="source",
            business_keys=["customer_id"],
            bucket_column="customer_id",
            datetime_columns={"event_ts": "EVENT"},
        )

    assert "_pipeline_run_id" in out.columns
    assert "_business_key_hash" not in out.columns
    assert "_row_hash" not in out.columns
    assert "_partition_bucket" not in out.columns
    assert "_sample_bucket" not in out.columns
    assert "_row_ingest_id" not in out.columns
    assert "EVENT_DATE_UTC8" not in out.columns
