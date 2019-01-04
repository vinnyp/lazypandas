import unittest
import pandas as pd
import numpy as np
import hackr
import pytest
import lazypandas as lp
import logging


class TestActions(unittest.TestCase):

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
