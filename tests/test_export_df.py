import unittest
import pandas as pd
import numpy as np
import pytest
import lazypandas as lp
import logging
import glob
import os


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
        lp.path_out = './tests/file_output/'

        return

    def test_typeerror_input_df(self):
        with pytest.raises(TypeError):
            lp.export_df('df')

    def test_typeerror_input_label(self):
        with pytest.raises(TypeError):
            lp.export_df(self.df, label=1, trace=False)

    def test_typeerror_input_index(self):
        with pytest.raises(TypeError):
            lp.export_df(self.df, show_index='yes')

    def test_typeerror_input_trace(self):
        with pytest.raises(TypeError):
            lp.export_df(self.df, label='df_account', trace='yes')

    def test_final_exported(self):
        label = "random_numbers"

        lp.export_df(self.df, label=label, trace=False)

        expected_file = lp.path_out + lp.timestamp_label + label + '.csv'
        created_file = glob.glob(expected_file).pop()

        assert expected_file == created_file

    def test_trace_exported(self):
        lp.export_df(self.df)
        lp.export_df(self.df)
        lp.export_df(self.df)
        lp.export_df(self.df)

        export_count = 4

        all_files = glob.glob(os.path.join(lp.path_out, lp.timestamp_label + 'iteration_' + '*.csv'))
        file_count = len(all_files)

        assert export_count == file_count


if __name__ == '__main__':
    unittest.main()
