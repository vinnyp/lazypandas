import datetime
import glob
import os
import pandas as pd
import logging


class Export(object):
    _timestamp_format = "%Y%m%d-%H%M%S-"
    _timestamp_now = datetime.datetime.today()
    _timestamp_label = _timestamp_now.strftime(_timestamp_format)
    _path_out = './'
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = super(Export, cls).__new__(cls, *args, **kwargs)
            cls.logger = logging.getLogger(__name__)
        return cls._singleton

    @property
    def path_out(self):
        return self._path_out

    @path_out.setter
    def path_out(self, value):
        self._path_out = value
        return

    @property
    def timestamp_label(self):
        return self._timestamp_label

    @staticmethod
    def _file_exists(file_name):
        file = glob.glob(os.path.join(file_name))
        exists = False

        if len(file) > 0:
            exists = True

        return exists

    def export_df(self, df, label='', show_index=False, trace=True, *args, **kwargs):
        self.logger.info("Export path: %s", self.path_out)

        if label == '':
            label = 'iteration_'

        if not isinstance(df, pd.DataFrame):
            raise TypeError('Expected type DataFrame, not ' + str(type(df)))

        if not isinstance(label, str):
            raise TypeError('Expected type str, not ' + str(type(label)))

        if not isinstance(show_index, bool):
            raise TypeError('Expected type bool, not ' + str(type(show_index)))

        if not isinstance(trace, bool):
            raise TypeError('Expected type bool, not ' + str(type(trace)))

        all_files = glob.glob(os.path.join(self.path_out, self.timestamp_label + label + '*.csv'))

        file_count = len(all_files)
        self.logger.info("Previous versions found: %s", file_count)

        buffer = ''

        if trace:
            try:
                buffer = self.path_out + self.timestamp_label + label + str(file_count + 1) + '.csv'
                df.to_csv(path_or_buf=buffer, index=show_index, *args, **kwargs)
            except Exception as e:
                self.logger.exception(self, "Exception: ", e)

        elif not trace:
            try:
                buffer = self.path_out + self.timestamp_label + label + '.csv'
                df.to_csv(path_or_buf=buffer, index=show_index, *args, **kwargs)
            except Exception as e:
                self.logger.exception(self, "Exception: ", e)

        file_exists = self._file_exists(buffer)

        if not file_exists:
            raise IOError("Exported file not found.")
        else:
            self.logger.info('Exported trace: %s', buffer)
            print('Exported: ' + buffer)

        return
