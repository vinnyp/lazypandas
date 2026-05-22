import numpy as np
import pandas as pd
import pytest

import lazypandas as lp


def _sample_df():
    return pd.DataFrame(np.random.randn(5, 2), columns=["A", "B"])


def test_b2_import_df_missing_file_raises_indexerror(tmp_path):
    """B2: logger.exception was wrapping IndexError into TypeError."""
    # Seed the import dir with one unrelated csv so the directory is not empty.
    # Write directly with pandas to avoid relying on export_df (which has B4 path bug
    # fixed in a later task).
    _sample_df().to_csv(tmp_path / "seed.csv", index=False)
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)

    with pytest.raises(IndexError):
        lp.import_df("not_a_real_file.csv")


def test_b3_export_df_handles_exception_correctly(tmp_path, monkeypatch):
    """B3: logger.exception(self, ...) crashes when the export path is unwritable."""
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)

    # Force pandas.to_csv to raise so the except branch is exercised
    import pandas as pd

    def boom(*args, **kwargs):
        raise OSError("disk on fire")

    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)

    # Today this raises TypeError from the broken logger.exception(self, ...) call,
    # masking the IOError("Exported file not found.") that the function intends.
    with pytest.raises((OSError, IOError)):
        lp.export_df(_sample_df(), label="boomtest", trace=False)


def test_b1_import_df_logs_correct_row_count(tmp_path, caplog):
    """B1: import_df logs len(file) (filename length) instead of len(df)."""
    df = _sample_df()  # 5 rows
    # Write directly with pandas to avoid relying on export_df (B4 path bug
    # fixed in a later task).
    df.to_csv(tmp_path / "rows_check.csv", index=False)
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)

    import logging

    with caplog.at_level(logging.INFO, logger="lazypandas.io"):
        lp.import_df("rows_check.csv")

    # Must log "Total rows: 5", not the length of the file path string.
    assert any("Total rows: 5" in rec.getMessage() for rec in caplog.records)


def test_b4_export_df_works_without_trailing_slash(tmp_path):
    """B4: string-concatenated paths break when path_out lacks a trailing slash."""
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Set path_out WITHOUT a trailing slash on purpose.
    lp.state.path_out = str(out_dir)
    lp.state.path_in = str(out_dir)

    lp.export_df(_sample_df(), label="noslash", trace=False)

    # File must land inside out_dir, not at out_dir's parent with a concat'd name.
    found = list(out_dir.glob("*noslash*.csv"))
    assert len(found) == 1, f"Expected exactly one csv inside {out_dir}, found {found}"


def test_b6_import_df_raises_on_ambiguous_match(tmp_path):
    """B6: silently popping last of multiple matches is dangerous."""
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)
    df = _sample_df()
    lp.export_df(df, label="report_v1", trace=False)
    lp.export_df(df, label="report_v2", trace=False)

    with pytest.raises(ValueError, match="ambiguous"):
        lp.import_df("report")  # matches both


def test_b6_import_df_single_match_still_works(tmp_path):
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)
    lp.export_df(_sample_df(), label="unique_label", trace=False)
    df = lp.import_df("unique_label.csv")
    assert len(df) == 5


def test_module_level_api_still_works(tmp_path):
    lp.state.path_out = str(tmp_path)
    lp.state.path_in = str(tmp_path)
    lp.export_df(_sample_df(), label="moduleapi", trace=False)
    df = lp.import_df("moduleapi.csv")
    assert len(df) == 5
