import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

import lazypandas as lp


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        np.random.randn(10, 3),
        columns=["A", "B", "C"],
        index=pd.date_range("1/1/2000", periods=10),
    )


@pytest.fixture
def io_dir(tmp_path):
    lp.state.path_in = str(tmp_path)
    lp.state.path_out = str(tmp_path)
    return tmp_path


def test_file_not_found(io_dir, sample_df):
    lp.export_df(sample_df, label="seed", trace=False)
    with pytest.raises(IndexError):
        lp.import_df("users.csv")


def test_file_imported(sample_df, io_dir):
    lp.export_df(sample_df, label="accounts", trace=False)
    df = lp.import_df("accounts.csv")
    assert len(df) == 10


def test_file_imported_contents_match(sample_df, io_dir):
    """T5: round-trip assertion using assert_frame_equal."""
    lp.export_df(sample_df, label="roundtrip", trace=False, show_index=True)
    df = lp.import_df("roundtrip.csv")
    assert_frame_equal(
        df.iloc[:, 1:].reset_index(drop=True),
        sample_df.reset_index(drop=True),
        check_dtype=False,
    )


def test_invalid_path():
    with pytest.raises(NotADirectoryError):
        lp.state.path_in = "not_a_valid_path"
