"""Foundational Spark writing to configured Lakehouse Files destinations."""
from __future__ import annotations

import sys
from uuid import uuid4

from .shared import (
    lakehouse_file_filesystem,
    repartition_dataframe_for_write,
    resolve_configured_file_path,
    validate_dataframe_writer,
    validate_file_write,
)


_MAX_SINGLE_FILE_ROWS = 1_000_000
_MAX_SINGLE_FILE_BYTES = 100_000_000


def write_lakehouse_file(
    dataframe, relative_path, *, store="Silver", file_format="parquet", mode="overwrite",
    write_options=None, repartition_by=None, verbose=True, context=None,
):
    """Write CSV, Parquet or newline-delimited JSON beneath configured Files.

    Parameters
    ----------
    dataframe : pyspark.sql.DataFrame
        Prepared input; no profiling, scanning or metadata persistence occurs.
    relative_path : str
        Exact nested path beneath Files, without absolute paths or selectors.
    store : str, default="Silver"
        Lakehouse key from 00_env_config.
    file_format : {"csv", "parquet", "json"}
        Spark output format.
    mode : {"overwrite", "append_all"}
        Overwrite replaces the destination; append_all adds data to a dataset folder only.
    write_options : dict, optional
        Spark writer options, such as header, sep or compression. Destination,
        mode and output layout overrides are rejected.
    repartition_by : int or str or list or tuple, optional
        Same Spark repartitioning conventions as write_lakehouse_table. Applied
        before staging; a small export then coalesces to one part, while distributed
        overflow and append_all preserve the requested repartitioning.
    verbose : bool, default=True
        Print logical destination on completion.
    context : dict, optional
        Fabric runtime override; Spark belongs to the supplied DataFrame.

    Returns
    -------
    dict
        Actual resolved_path, relative_path, published, publication_status,
        file_format, actual output_layout, mode, file_count, output_bytes,
        overflow_occurred, overflow_reason
        (row_limit, byte_limit or None) and write_metrics. Row commit counts
        are unknown; file_count and output_bytes describe the resulting target.

    Notes
    -----
    Overwrite automatically attempts one physical file. Internal safety policy
    selects a distributed dataset folder at the exact same path above 1,000,000
    rows or 100,000,000 encoded bytes (100 MB). These limits are implementation
    policy, not a Microsoft OneLake file-size limit. append_all always writes a
    dataset folder and rejects an existing physical file. No rows are truncated.
    Use deterministic input from stable sources across the count and write actions;
    byte overflow re-executes the original DataFrame after discarding staging.
    Lazy reads from the destination finish before overwrite moves that destination.
    Single-file output uses one executor, a bounded count, temporary Spark output
    and a filesystem rename. It never collects business rows on the driver.
    Coalescing limits parallelism and can exhaust executor memory for wide rows;
    row and encoded-byte safeguards do not bound executor working memory. The
    byte check occurs after staging, before publication. Only row/byte limit
    checks trigger overflow; unrelated failures propagate without fallback. Single CSV/JSON uses uncompressed
    output; compressed CSV/JSON requires dataset-folder output. Overwrite replaces an existing
    file or folder only after staging succeeds; rename/replace is not transactional.
    Dataset overwrite also stages all rows before replacing the target, so lazy
    reads of that target finish before it is moved. Existing output is renamed to
    a unique backup and restored when publication fails and the target is absent.
    Failed/ambiguous publication retains staging and backup recovery paths on the
    raised exception; never delete these until the output has been inspected.
    Concurrent writers to the same physical path or overlapping folders are
    unsupported, including aliases through different stores. There is no distributed
    lock. Serialize writers externally and coordinate readers: replacement can
    expose a temporary gap between renames. Resolve ambiguous failures before
    retrying. Production use requires signed-in Fabric validation of permissions,
    shortcut support, rename outcomes, rollback and recovery.
    Temporary output is
    removed after successful publication or failures before publication begins. Empty frames use Spark's native empty output.
    Permission and read-only/unsupported shortcut failures propagate with a clear
    destination error. SharePoint shortcuts are not assumed writable; no fallback
    destination is used. Fabric Hadoop rename semantics require live validation.

    Examples
    --------
    >>> write_lakehouse_file(dataframe=final_df, relative_path="Exports/orders.csv",
    ...     store="Silver", file_format="csv", write_options={"header": True})
    >>> write_lakehouse_file(final_df, "Exports/orders.json", file_format="json",
    ...     mode="overwrite")

    """
    validate_dataframe_writer(dataframe)
    mode, options = validate_file_write(relative_path, file_format, mode, write_options)
    frame = repartition_dataframe_for_write(dataframe, repartition_by)
    _, relative_path, path = resolve_configured_file_path(store, relative_path, context=context)
    fs, target, path_type = lakehouse_file_filesystem(dataframe, path, context=context)
    staging = None
    retain_staging = False
    actual_single_file = mode != "append_all"
    overflow_reason = None
    try:
        if mode != "overwrite" and fs.exists(target) and fs.isFile(target):
            raise ValueError("Destination layout is a physical file; append_all requires a dataset folder.")
        if actual_single_file:
            if dataframe.limit(_MAX_SINGLE_FILE_ROWS + 1).count() > _MAX_SINGLE_FILE_ROWS:
                actual_single_file = False
                overflow_reason = "row_limit"
            else:
                single_options = {**options, "maxRecordsPerFile": 0}
                if file_format in {"csv", "json"}:
                    single_options["compression"] = "none"
                staging = path_type(path + ".fabricops-" + uuid4().hex)
                frame.coalesce(1).write.format(file_format).mode("errorifexists").options(**single_options).save(str(staging))
                parts = [entry for entry in fs.listStatus(staging) if entry.isFile() and entry.getPath().getName().startswith("part-")]
                if len(parts) != 1:
                    raise RuntimeError("Single-file staging did not produce exactly one data part.")
                if parts[0].getLen() > _MAX_SINGLE_FILE_BYTES:
                    # No publication has begun. Discard only this unsuccessful staging.
                    if not fs.delete(staging, True) and fs.exists(staging):
                        raise RuntimeError("Filesystem refused oversized single-file staging cleanup.")
                    staging = None
                    actual_single_file = False
                    overflow_reason = "byte_limit"
        if actual_single_file:
            retain_staging = True
            published = _publish_staged(fs, parts[0].getPath(), target, mode=mode, path_type=path_type)
            retain_staging = False
        elif mode == "overwrite":
            # Evaluate every lazy input before moving or replacing the destination.
            staging = path_type(path + ".fabricops-" + uuid4().hex)
            frame.write.format(file_format).mode("errorifexists").options(**options).save(str(staging))
            retain_staging = True
            published = _publish_staged(fs, staging, target, mode=mode, path_type=path_type)
            retain_staging = False
        else:
            frame.write.format(file_format).mode("append").options(**options).save(path)
            published = True
        result = _result(fs, target, path, relative_path, file_format, actual_single_file, mode, published,
                         overflow_reason=overflow_reason)
    except (ValueError, FileExistsError) as exc:
        if retain_staging:
            exc.recovery_paths = [str(staging), *getattr(exc, "recovery_paths", ())]
        else:
            retain_staging = False  # Pre-publication validation/collision rejection.
        raise
    except Exception as exc:
        failure = RuntimeError("Lakehouse Files write failed; check destination permissions and shortcut write/rename support.")
        if retain_staging:
            recovery = [str(staging), *getattr(exc, "recovery_paths", ())]
            failure.recovery_paths = list(dict.fromkeys(recovery))
            failure.args = (str(failure) + " Recovery paths retained for inspection: " + ", ".join(failure.recovery_paths),)
        failure.output_layout = "single_file" if actual_single_file else "dataset_folder"
        failure.overflow_occurred = overflow_reason is not None
        failure.overflow_reason = overflow_reason
        if getattr(exc, "published", False):
            failure.published = True
            failure.resolved_path = path
            failure.publication_status = "published"
            failure.write_metrics = _result(fs, target, path, relative_path, file_format, actual_single_file, mode, True)["write_metrics"]
        raise failure from exc
    finally:
        if staging is not None and not retain_staging:
            pending = sys.exception()
            try:
                removed = fs.delete(staging, True)
                if not removed and fs.exists(staging):
                    raise RuntimeError("Filesystem refused temporary file-output cleanup.")
            except Exception as cleanup:
                if pending is not None:
                    pending.add_note("Temporary file-output cleanup also failed; inspect the staging destination.")
                    pending.recovery_paths = list(dict.fromkeys([str(staging), *getattr(pending, "recovery_paths", ())]))
                else:
                    failure = RuntimeError("File publication completed but temporary output cleanup failed.")
                    failure.published = result["published"]
                    failure.resolved_path = path
                    failure.publication_status = result["publication_status"]
                    failure.write_metrics = result["write_metrics"]
                    failure.output_layout = result["output_layout"]
                    failure.overflow_occurred = result["overflow_occurred"]
                    failure.overflow_reason = result["overflow_reason"]
                    failure.recovery_paths = [str(staging)]
                    raise failure from cleanup
    if verbose and not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Written to → Object: Lakehouse | Store: {store} | Area: Files | Path: {relative_path}")
    return result


def _result(fs, target, path, relative_path, file_format, single_file, mode, published, *, overflow_reason=None):
    """Describe physical output without claiming transactional row metrics."""
    metrics = {"rows_committed": None, "measurement_source": "filesystem",
               "file_count": None, "output_bytes": None}
    try:
        files = fs.listFiles(target, True)
        count = size = 0
        while files.hasNext():
            entry = files.next()
            if single_file or not entry.getPath().getName().startswith(("_", ".")):
                count += 1
                size += entry.getLen()
        metrics.update(file_count=count, output_bytes=size)
    except Exception:
        pass  # Publication succeeded even if optional listing metrics are unavailable.
    return {"resolved_path": path, "relative_path": relative_path, "file_format": file_format,
            "output_layout": "single_file" if single_file else "dataset_folder", "mode": mode,
            "published": published, "publication_status": "published" if published else "not_published",
            "overflow_occurred": overflow_reason is not None, "overflow_reason": overflow_reason,
            "file_count": metrics["file_count"], "output_bytes": metrics["output_bytes"],
            "write_metrics": metrics}


def _publish_staged(fs, source, target, *, mode, path_type):
    """Replace a completed artifact with rollback and retained recovery copies."""
    backup = None
    try:
        if fs.exists(target):
            if mode != "overwrite":
                raise FileExistsError("Lakehouse Files destination already exists.")
            backup_is_directory = not fs.isFile(target)
            backup = path_type(str(target) + ".fabricops-backup-" + uuid4().hex)
            if not fs.rename(target, backup):
                raise RuntimeError("Filesystem refused to preserve existing output before publication.")
        fs.mkdirs(target.getParent())
        if not fs.rename(source, target):
            raise RuntimeError("Filesystem refused staged output publication rename.")
    except Exception as exc:
        if backup is not None:
            try:
                if fs.exists(backup) and not fs.exists(target):
                    if not fs.rename(backup, target):
                        exc.add_note("Backup restoration failed; recovery copies were retained.")
            except Exception:
                exc.add_note("Backup restoration could not be confirmed; recovery copies were retained.")
            exc.recovery_paths = [str(backup)]
        raise
    if backup is not None:
        try:
            if not fs.delete(backup, backup_is_directory) and fs.exists(backup):
                raise RuntimeError("Filesystem refused backup cleanup.")
        except Exception as exc:
            failure = RuntimeError("Output published but previous-output backup cleanup failed.")
            failure.published = True
            failure.recovery_paths = [str(backup)]
            raise failure from exc
    return True
