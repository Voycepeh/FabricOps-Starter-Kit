"""Regression checks for the portable FabricOps pipeline builder."""

import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract
SKILL = Path(__file__).parents[2] / ".agents" / "skills" / "fabricops-pipeline-builder"
INCREMENTAL = (
    'read_mode="incremental",\n'
    '    target_store="Silver",\n'
    '    target_schema="demo",\n'
    '    target_table_name="orders",\n'
    '    read_parameters={"watermark_column": "updated_at"},'
)


@pytest.fixture
def installed_skill(tmp_path):
    """Copy the skill outside the source tree for CLI validation."""
    return shutil.copytree(SKILL, tmp_path / ".agents" / "skills" / SKILL.name)


def _validate(skill, edits=(), *, stores=("Bronze", "Silver"), expected_version=None):
    item = skill / "examples" / "bronze_to_silver.Notebook"
    source = item / "notebook-content.py"
    code = source.read_text(encoding="utf-8")
    for original, replacement in edits:
        assert original in code
        code = code.replace(original, replacement, 1)
    source.write_text(code, encoding="utf-8")
    args = [
        sys.executable, str(skill / "scripts" / "validate.py"), str(item),
        "--fabricops-version", expected_version or version("fabricops-kit"),
    ]
    for store in stores:
        args.extend(("--store", store))
    return subprocess.run(args, cwd=skill.parents[2], capture_output=True, text=True, check=False)


def test_example_is_an_independent_git_notebook(installed_skill):
    """The copied example passes the CLI without using the source checkout as cwd."""
    result = _validate(installed_skill)
    assert result.returncode == 0, result.stderr
    assert "Dry Run | 1 Read(s), 1 Write(s)" in result.stdout


def test_incremental_can_feed_matching_scd1_target(installed_skill):
    """An explicit Incremental Read bound to the declared table target passes."""
    result = _validate(installed_skill, [('read_mode="full",', INCREMENTAL)])
    assert result.returncode == 0, result.stderr


def test_disjoint_file_paths_can_share_a_store(installed_skill):
    """A matching filename prefix alone does not make two exact paths overlap."""
    result = _validate(installed_skill, [
        ('schema="demo",\n    table_name="order_events",', 'relative_path="input/orders.csv", file_format="csv",'),
        ('store="Silver",\n    schema="demo",\n    table_name="orders",', (
            'store="Bronze", relative_path="input/orders.csv.parquet", file_format="parquet",'
        )),
        ('write_mode="scd1",\n    write_parameters={"key_columns": ["order_id"]},', 'write_mode="overwrite",'),
    ])
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(("edits", "message"), [
    ([("# ## Transform", "# ## Read")], "Duplicate section Read"),
    ([("synapse_pyspark", "python")], "Use the synapse_pyspark kernel"),
    ([("orchestrate_read, orchestrate_write", "pipeline_read, orchestrate_write")], "pipeline entry points"),
    ([('read_mode="full",', 'read_mode="full", unsupported_option=True,')], "unexpected keyword"),
    ([('store="Bronze",', 'store="Unknown",')], "confirmed store alias"),
    ([('schema="demo",', '')], "Set schema explicitly"),
    ([('pipeline_mode="Dry Run"', 'pipeline_mode="Governed"')], "explicitly reviewed Ungoverned"),
    ([('write_parameters={"key_columns": ["order_id"]},', '')], "requires nonempty, distinct key_columns"),
    ([('write_mode="scd1"', 'write_mode="scd2"')], "requires effective_column"),
    ([('read_mode="full",', INCREMENTAL.replace('    read_parameters={"watermark_column": "updated_at"},', ''))],
     "requires an explicit read_parameters.watermark_column"),
    ([('read_mode="full",', INCREMENTAL.replace('target_table_name="orders"', 'target_table_name="other"'))],
     "must match a table Write"),
    ([('read_mode="full",', INCREMENTAL), ('write_mode="scd1"', 'write_mode="overwrite"')],
     "cannot feed whole-table Overwrite"),
    ([('store="Silver"', 'store="Bronze"'), ('table_name="orders"', 'table_name="ORDER_EVENTS"')],
     "target overlaps a declared source"),
    ([("latest_order = Window", "sources['orders']['dataframe'].write.saveAsTable('demo.other')\nlatest_order = Window")],
     "Use orchestrate_write for persistence"),
    ([("finalize_pipeline(pipeline)", "finalize_pipeline()")], "Pass the pipeline session"),
])
def test_invalid_candidates_fail_before_execution(installed_skill, edits, message):
    """Return actionable failures without running notebook cells."""
    result = _validate(installed_skill, edits)
    assert result.returncode == 1
    assert message in result.stderr


def test_validation_checks_the_installed_version(installed_skill):
    """Avoid a successful validation report for a different installed release."""
    result = _validate(installed_skill, expected_version="0.0.0")
    assert result.returncode == 1
    assert "differs from expected 0.0.0" in result.stderr
