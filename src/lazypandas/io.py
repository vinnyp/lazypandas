import datetime
import glob
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pandas as pd

logger = logging.getLogger(__name__)

_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S-"


def _validate_dir(value: str) -> str:
    if not Path(value).is_dir():
        raise NotADirectoryError(f"Not a valid directory: {value!r}")
    return value


@dataclass
class _State:
    _path_in: str = "./"
    _path_out: str = "./"
    # NOTE: timestamp_label is computed once per import session and reused.
    # To rotate it manually in a running process, reassign lp.state.timestamp_label.
    timestamp_label: str = field(
        default_factory=lambda: datetime.datetime.now().strftime(_TIMESTAMP_FORMAT)
    )

    @property
    def path_in(self) -> str:
        return self._path_in

    @path_in.setter
    def path_in(self, value: str) -> None:
        self._path_in = _validate_dir(value)

    @property
    def path_out(self) -> str:
        return self._path_out

    @path_out.setter
    def path_out(self, value: str) -> None:
        self._path_out = _validate_dir(value)


state = _State()


def _file_exists(file_name: Path) -> bool:
    return file_name.is_file()


def export_df(
    df: pd.DataFrame,
    label: str = "",
    show_index: bool = False,
    trace: bool = True,
    *args: Any,
    **kwargs: Any,
) -> None:
    logger.info("Export path: %s", state.path_out)

    if label == "":
        label = "iteration_"

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    if not isinstance(label, str):
        raise TypeError(f"label must be str, got {type(label).__name__}")
    if not isinstance(show_index, bool):
        raise TypeError(f"show_index must be bool, got {type(show_index).__name__}")
    if not isinstance(trace, bool):
        raise TypeError(f"trace must be bool, got {type(trace).__name__}")

    out_dir = Path(state.path_out)
    all_files = glob.glob(str(out_dir / f"{state.timestamp_label}{label}*.csv"))
    file_count = len(all_files)
    logger.info("Previous versions found: %s", file_count)

    if trace:
        path = out_dir / f"{state.timestamp_label}{label}{file_count + 1:02d}.csv"
    else:
        path = out_dir / f"{state.timestamp_label}{label}.csv"

    to_csv_kwargs = {"path_or_buf": str(path), "index": show_index, **kwargs}
    try:
        df.to_csv(*args, **to_csv_kwargs)
    except Exception:
        logger.exception("Error writing CSV")
        raise

    if not _file_exists(path):
        raise OSError(f"Exported file not found: {path}")
    logger.info("Exported: %s", path)


def import_df(file_name: str, *args: Any, **kwargs: Any) -> pd.DataFrame:
    in_dir = Path(state.path_in)
    all_files = sorted(glob.glob(str(in_dir / "*.csv")))

    if not all_files:
        logger.info("Import directory is empty: %s", in_dir)
        raise OSError(f"Import directory is empty: {in_dir}")

    matches = [path for path in all_files if file_name in path]
    if not matches:
        logger.error("No file matching %r in %s", file_name, in_dir)
        raise IndexError(f"No file matching {file_name!r} in {in_dir}")
    if len(matches) > 1:
        raise ValueError(
            f"ambiguous match for {file_name!r}: found {len(matches)} files: {matches}"
        )

    file_path = matches[0]
    read_csv_kwargs = {"low_memory": False, "encoding": "utf-8", **kwargs}
    df = cast(pd.DataFrame, pd.read_csv(file_path, *args, **read_csv_kwargs))
    logger.info("Imported file: %s", file_path)
    logger.info("Total rows: %d", len(df))
    return df


def export_df_versioned(
    df: pd.DataFrame,
    label: str = "",
    show_index: bool = False,
    *args: Any,
    **kwargs: Any,
) -> None:
    return export_df(df, label, show_index, True, *args, **kwargs)


def export_df_overwrite(
    df: pd.DataFrame,
    label: str = "",
    show_index: bool = False,
    *args: Any,
    **kwargs: Any,
) -> None:
    return export_df(df, label, show_index, False, *args, **kwargs)
