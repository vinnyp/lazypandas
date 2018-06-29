import unittest
import pandas as pd
import numpy as np
import pytest
import lazypandas as lp


class TestExportDf(unittest.TestCase):

    def setUp(self):

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


if __name__ == '__main__':
    unittest.main()
