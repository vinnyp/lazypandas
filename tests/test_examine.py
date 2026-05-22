import numpy as np
import pandas as pd
import pytest

import lazypandas as lp


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        data={
            "A": ["Watermelon", "Cherry", "Apple", "Banana", np.nan, np.nan, np.nan,
                  "Blueberry", "Strawberry", "Grape"],
            "B": [1, 2, 3, np.nan, 8, 2, 4, 1, 22, 1],
            "C": ["Blue", "Yellow", "Green", "Red", "Magenta", "Orange", "Pink",
                  "Purple", np.nan, np.nan],
        },
        columns=["A", "B", "C"],
        index=pd.date_range("1/1/2000", periods=10),
    )


def test_missing_summary_returns_per_column_counts(sample_df):
    summary = lp.missing_summary(sample_df)
    assert isinstance(summary, pd.Series)
    assert summary["A"] == 3
    assert summary["B"] == 1
    assert summary["C"] == 2


def test_missing_summary_type_error_on_non_dataframe():
    with pytest.raises(TypeError):
        lp.missing_summary("not a df")


def test_missing_values_total_count(sample_df):
    assert lp.missing_values(sample_df) == 6


def test_missing_values_single_column(sample_df):
    assert lp.missing_values(sample_df, columns=["A"]) == 3


def test_missing_values_multi_column(sample_df):
    assert lp.missing_values(sample_df, columns=["A", "B"]) == 4
    assert lp.missing_values(sample_df, columns=["A", "B", "C"]) == 6


def test_missing_values_type_error_on_non_dataframe():
    with pytest.raises(TypeError):
        lp.missing_values("not a df")


def test_missing_values_bad_column(sample_df):
    with pytest.raises(KeyError):
        lp.missing_values(sample_df, columns=["nope"])
