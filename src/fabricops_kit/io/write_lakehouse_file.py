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


def write_lakehouse_file(
    dataframe, relative_path, *, store="Silver", file_format="parquet", mode="errorifexists",
    write_options=None, repartition_by=None, single_file=False,
    max_single_file_rows=1000000, max_single_file_bytes=134217728, verbose=True, context=None,
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
    mode : {"errorifexists", "overwrite", "append", "ignore"}
        Spark collision policy. Append is supported only for dataset folders.
    write_options : dict, optional
        Spark writer options, such as header, sep or compression. Destination,
        mode and output layout overrides are rejected.
    repartition_by : int or str or list or tuple, optional
        Same Spark repartitioning conventions as write_lakehouse_table.
    single_file : bool, default=False
        Explicitly produce one named artifact with a matching format extension.
        Otherwise the path is a dataset directory, even if it has an extension.
    max_single_file_rows : int, default=1000000
        Single-file input row limit, checked with a bounded Spark count.
    max_single_file_bytes : int, default=134217728
        Maximum staged output bytes before publishing one artifact.
    verbose : bool, default=True
        Print logical destination on completion.
    context : dict, optional
        Fabric runtime override; Spark belongs to the supplied DataFrame.

    Returns
    -------
    dict
        Actual resolved_path, relative_path, published, publication_status,
        file_format, output_layout, mode and write_metrics. Row commit counts
        are unknown; file_count and output_bytes describe the resulting target.

    Notes
    -----
    Single-file output uses one executor, a bounded count, temporary Spark output
    and a filesystem rename. It never collects business rows on the driver.
    Coalescing limits parallelism and can exhaust executor memory for wide rows;
    row and encoded-byte safeguards do not bound executor working memory. The
    byte check occurs after staging, before publication. Single CSV/JSON uses uncompressed
    output; compressed CSV/JSON requires dataset-folder output. Overwrite replaces an existing
    artifact only after staging succeeds; rename/replace is not transactional.
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
    ...     single_file=True, mode="overwrite")

    """
    validate_dataframe_writer(dataframe)
    mode, options = validate_file_write(relative_path, file_format, mode, write_options,
        single_file=single_file, repartition_by=repartition_by,
        max_single_file_rows=max_single_file_rows, max_single_file_bytes=max_single_file_bytes)
    frame = repartition_dataframe_for_write(dataframe, repartition_by)
    if single_file:
        options["maxRecordsPerFile"] = 0
        if file_format in {"csv", "json"}:
            options["compression"] = "none"
    _, relative_path, path = resolve_configured_file_path(store, relative_path, context=context)
    fs, target, path_type = lakehouse_file_filesystem(dataframe, path, context=context)
    staging = None
    retain_staging = False
    try:
        exists = fs.exists(target)
        if exists and fs.isFile(target) != single_file:
            raise ValueError("Destination layout differs from requested single-file/dataset-folder output.")
        if exists and mode == "errorifexists":
            raise FileExistsError("Lakehouse Files destination already exists.")
        if exists and mode == "ignore":
            return _result(fs, target, path, relative_path, file_format, single_file, mode, False)
        if single_file:
            if dataframe.limit(max_single_file_rows + 1).count() > max_single_file_rows:
                raise ValueError("Single-file row limit exceeded; use dataset-folder output.")
            staging = path_type(path + ".fabricops-" + uuid4().hex)
            frame.coalesce(1).write.format(file_format).mode("errorifexists").options(**options).save(str(staging))
            parts = [entry for entry in fs.listStatus(staging) if entry.isFile() and entry.getPath().getName().startswith("part-")]
            if len(parts) != 1:
                raise RuntimeError("Single-file staging did not produce exactly one data part.")
            if parts[0].getLen() > max_single_file_bytes:
                raise ValueError("Single-file byte limit exceeded; use dataset-folder output.")
            retain_staging = True
            published = _publish_staged(fs, parts[0].getPath(), target, mode=mode, path_type=path_type, single_file=True)
            retain_staging = False
        elif mode == "overwrite":
            # Evaluate every lazy input before moving or replacing the destination.
            staging = path_type(path + ".fabricops-" + uuid4().hex)
            frame.write.format(file_format).mode("errorifexists").options(**options).save(str(staging))
            retain_staging = True
            _publish_staged(fs, staging, target, mode=mode, path_type=path_type, single_file=False)
            retain_staging = False
        else:
            frame.write.format(file_format).mode(mode).options(**options).save(path)
        result = _result(fs, target, path, relative_path, file_format, single_file, mode, published if single_file else True)
    except (ValueError, FileExistsError) as exc:
        if retain_staging and getattr(exc, "recovery_paths", None):
            exc.recovery_paths = [str(staging), *exc.recovery_paths]
        else:
            retain_staging = False  # Pre-publication validation/collision rejection.
        raise
    except Exception as exc:
        failure = RuntimeError("Lakehouse Files write failed; check destination permissions and shortcut write/rename support.")
        if retain_staging:
            recovery = [str(staging), *getattr(exc, "recovery_paths", ())]
            failure.recovery_paths = list(dict.fromkeys(recovery))
            failure.args = (str(failure) + " Recovery paths retained for inspection: " + ", ".join(failure.recovery_paths),)
        if getattr(exc, "published", False):
            failure.published = True
            failure.resolved_path = path
            failure.publication_status = "published"
            failure.write_metrics = _result(fs, target, path, relative_path, file_format, single_file, mode, True)["write_metrics"]
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
                else:
                    failure = RuntimeError("File publication completed but temporary output cleanup failed.")
                    failure.published = result["published"]
                    failure.resolved_path = path
                    failure.publication_status = result["publication_status"]
                    failure.write_metrics = result["write_metrics"]
                    raise failure from cleanup
    if verbose and not (context or {}).get("_fabricops_suppress_io_log"):
        print(f"Written to → Object: Lakehouse | Store: {store} | Area: Files | Path: {relative_path}")
    return result


def _result(fs, target, path, relative_path, file_format, single_file, mode, published):
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
            "published": published, "publication_status": "published" if published else "ignored",
            "write_metrics": metrics}


def _publish_staged(fs, source, target, *, mode, path_type, single_file):
    """Replace a completed artifact with rollback and retained recovery copies."""
    backup = None
    try:
        if fs.exists(target):
            if fs.isFile(target) != single_file:
                raise ValueError("Destination layout differs from requested output.")
            if mode == "ignore":
                return False
            if mode != "overwrite":
                raise FileExistsError("Lakehouse Files destination already exists.")
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
            if not fs.delete(backup, not single_file) and fs.exists(backup):
                raise RuntimeError("Filesystem refused backup cleanup.")
        except Exception as exc:
            failure = RuntimeError("Output published but previous-output backup cleanup failed.")
            failure.published = True
            failure.recovery_paths = [str(backup)]
            raise failure from exc
    return True
