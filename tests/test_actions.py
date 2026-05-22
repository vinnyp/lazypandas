# tests/test_actions.py
import numpy as np
import pandas as pd
import pytest

import lazypandas as lp


def test_split_and_fill_backfills_target_from_source_split():
    """When target is NaN and source has 'A:B', split on ':' and put 'B' into target, 'A' back into source."""
    df = pd.DataFrame({
        "source": ["foo:bar", "baz:qux", "lone"],
        "target": [np.nan, np.nan, "preserved"],
    })
    result = lp.split_and_fill(df.copy(), source="source", target="target", separator=":")

    # Row 0: target gets "bar", source becomes "foo"
    assert result.loc[0, "source"] == "foo"
    assert result.loc[0, "target"] == "bar"
    # Row 1: target gets "qux", source becomes "baz"
    assert result.loc[1, "source"] == "baz"
    assert result.loc[1, "target"] == "qux"
    # Row 2: target already non-null, source must remain untouched (no separator in it)
    assert result.loc[2, "source"] == "lone"
    assert result.loc[2, "target"] == "preserved"


def test_split_and_fill_skips_rows_with_filled_target():
    df = pd.DataFrame({
        "source": ["foo:bar"],
        "target": ["already_set"],
    })
    result = lp.split_and_fill(df.copy(), source="source", target="target", separator=":")
    assert result.loc[0, "source"] == "foo:bar"  # unchanged
    assert result.loc[0, "target"] == "already_set"


def test_split_and_fill_skips_rows_with_null_source():
    df = pd.DataFrame({
        "source": [np.nan],
        "target": [np.nan],
    })
    result = lp.split_and_fill(df.copy(), source="source", target="target", separator=":")
    assert pd.isna(result.loc[0, "source"])
    assert pd.isna(result.loc[0, "target"])


def test_split_and_fill_returns_dataframe():
    df = pd.DataFrame({"source": ["x:y"], "target": [np.nan]})
    result = lp.split_and_fill(df, source="source", target="target", separator=":")
    assert isinstance(result, pd.DataFrame)


def test_split_and_fill_handles_non_string_source_gracefully():
    """Non-string eligible source values must not crash the call."""
    df = pd.DataFrame({
        "source": ["foo:bar", 42, "baz:qux"],
        "target": [np.nan, np.nan, np.nan],
    })
    result = lp.split_and_fill(df.copy(), source="source", target="target", separator=":")
    # String rows still split.
    assert result.loc[0, "source"] == "foo"
    assert result.loc[0, "target"] == "bar"
    assert result.loc[2, "source"] == "baz"
    assert result.loc[2, "target"] == "qux"
    # Non-string source left untouched; target stays NaN.
    assert result.loc[1, "source"] == 42
    assert pd.isna(result.loc[1, "target"])
