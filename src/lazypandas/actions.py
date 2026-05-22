"""Data-cleaning actions on DataFrames."""
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def split_and_fill(
    df: pd.DataFrame,
    source: str,
    target: str,
    separator: str,
) -> pd.DataFrame:
    """Backfill empty target column by splitting source on separator.

    For rows where ``target`` is NaN and ``source`` is non-null, splits
    ``source`` on ``separator`` and puts the second part into ``target``
    while keeping the first part in ``source``. Rows where target is
    already populated, or source is null, are left untouched.
    """
    null_target = df[target].isnull()
    populated_source = df[source].notnull()
    eligible = null_target & populated_source

    n = int(eligible.sum())
    logger.debug("split_and_fill: backfilling %d rows", n)

    if n and df[target].dtype != object:
        df[target] = df[target].astype(object)

    df.loc[eligible, target] = df.loc[eligible, source].apply(
        lambda x: x.split(separator)[1] if separator in x else None
    )
    df.loc[eligible, source] = df.loc[eligible, source].apply(
        lambda x: x.split(separator)[0]
    )

    return df
