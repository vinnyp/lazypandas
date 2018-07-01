import unittest
import pandas as pd
import numpy as np
import pytest
import lazypandas as lp
import logging
from pathlib import Path


class TestExportDf(unittest.TestCase):

    def setUp(self):

        # create the Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        self.df = pd.DataFrame(np.random.randn(10, 3), columns=['A', 'B', 'C'],
                               index=pd.date_range('1/1/2000', periods=10))
        self.df.name = 'Sample df'
        lp.path_in = './tests/file_output/'
        lp.path_out = './tests/file_output/'

        return

    def test_file_not_found(self):
        with pytest.raises(IndexError):
            lp.import_df('users.csv')

    def test_file_imported(self):
        lp.export_df(self.df, label='accounts', trace=False)
        df = lp.import_df('accounts.csv')

        assert len(df) > 0


if __name__ == '__main__':
    unittest.main()


def test_invalid_path():
    lp.path_in = 'not_a_valid_path'
    path = Path(lp.path_in).is_dir()

    assert (not path)
