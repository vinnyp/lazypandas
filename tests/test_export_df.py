import glob

import numpy as np
import pandas as pd
import pytest

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


def test_typeerror_input_df():
    with pytest.raises(TypeError):
        lp.export_df("not a dataframe")


def test_typeerror_input_label(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, label=1, trace=False)


def test_typeerror_input_index(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, show_index="yes")


def test_typeerror_input_trace(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, label="df_account", trace="yes")


def test_final_exported(sample_df, io_dir):
    label = "random_numbers"
    lp.export_df(sample_df, label=label, trace=False)
    expected = io_dir / f"{lp.state.timestamp_label}{label}.csv"
    assert expected.is_file()


def test_trace_exported(sample_df, io_dir):
    for _ in range(4):
        lp.export_df(sample_df)
    all_files = glob.glob(str(io_dir / f"{lp.state.timestamp_label}iteration_*.csv"))
    assert len(all_files) == 4


def test_invalid_path():
    with pytest.raises(NotADirectoryError):
        lp.state.path_out = "not_a_valid_path"
