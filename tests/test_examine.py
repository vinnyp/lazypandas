import unittest
import pandas as pd
import numpy as np
import pytest
import lazypandas as lp
import logging


class TestExamine(unittest.TestCase):

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

        self.df = pd.DataFrame(data={'A': ['Watermelon', 'Cherry', 'Apple', 'Banana', np.nan, np.nan, np.nan,
                                           'Blueberry', 'Strawberry', 'Grape'],
                                     'B': [1, 2, 3, np.nan, 8, 2, 4, 1, 22, 1],
                                     'C': ['Blue', 'Yellow', 'Green', 'Red', 'Magenta', 'Orange', 'Pink',
                                           'Purple', np.nan, np.nan]}, columns=['A', 'B', 'C'],
                               index=pd.date_range('1/1/2000', periods=10))
        self.df.name = 'Sample df'

        return

    def test_missing_summary(self):
        summary = lp.missing_summary(self.df)
        print(summary)
        assert len(self.df) > 0

    def test_missing_values(self):
        count = lp.missing_values(self.df)
        assert count == 6
        count = lp.missing_values(self.df, columns=['A'])
        assert count == 3
        count = lp.missing_values(self.df, columns=['A', 'B'])
        assert count == 4
        count = lp.missing_values(self.df, columns=['A', 'B', 'C'])
        assert count == 6

    def test_missing_summary_type(self):
        with pytest.raises(TypeError):
            lp.missing_summary('df')

    def test_missing_values_type(self):
        with pytest.raises(TypeError):
            lp.missing_values('df')

    def test_missing_values_column_type(self):
        with pytest.raises(Exception):
            lp.missing_values(self.df, columns=[1])
