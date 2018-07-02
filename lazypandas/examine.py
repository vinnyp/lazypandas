import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def missing_summary(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected type DataFrame, not type " + str(type(df)))

    num_rows = df.shape[0]
    num_missing = num_rows - df.count()
    logger.info(str(num_missing))

    return num_missing


def missing_values(df, columns=None):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected type DataFrame, not type " + str(type(df)))

    count = 0

    if columns is None:
        count = np.count_nonzero(df.isnull())
    else:
        try:
            count = np.count_nonzero(df[columns].isnull())
        except Exception as e:
            logger.exception("Columns not found. ", e)
            raise

    return count


def unique():
    raise NotImplementedError





