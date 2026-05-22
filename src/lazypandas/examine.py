"""Examine pandas DataFrames for missing values."""

from __future__ import annotations

import logging
from collections.abc import Iterable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def missing_summary(df: pd.DataFrame) -> pd.Series:
    """Per-column count of missing (NaN) values."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    num_missing: pd.Series = df.isnull().sum()
    logger.info("Missing-value summary: %s", num_missing.to_dict())
    return num_missing


def missing_values(df: pd.DataFrame, columns: Iterable[str] | None = None) -> int:
    """Total count of missing values across df, or a column subset."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    target = df if columns is None else df[list(columns)]
    return int(np.count_nonzero(target.isnull()))
