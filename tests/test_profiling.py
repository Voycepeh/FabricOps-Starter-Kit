from fabricops_kit.data_profiling import _get_profiled_columns, _is_min_max_supported_type


class FakeDTypesDataFrame:
    def __init__(self, dtypes):
        self.dtypes = dtypes


def test_get_profiled_columns_excludes_default_and_custom_columns():
    df = FakeDTypesDataFrame(
        [
            ("id", "int"),
            ("pipeline_ts", "timestamp"),
            ("status", "string"),
            ("custom_tech", "string"),
        ]
    )

    assert _get_profiled_columns(df, exclude_columns={"custom_tech"}) == ["id", "status"]


def test_is_min_max_supported_type_handles_supported_and_unsupported_types():
    assert _is_min_max_supported_type("int") is True
    assert _is_min_max_supported_type("timestamp") is True
    assert _is_min_max_supported_type("string") is True

    assert _is_min_max_supported_type("array<string>") is False
    assert _is_min_max_supported_type("struct<a:int>") is False
    assert _is_min_max_supported_type("map<string,int>") is False
