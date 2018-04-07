import abc
import os
import iso8601
import pandas as pd
from ..logger import Logger


class DataAPIInterface:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.log = Logger()

    def save_data_to_local(self, df, filepath, filename):
        fullpath = os.path.join(filepath, filename + '.csv')
        if os.path.isfile(fullpath):
            self.log.info('Append data to %s' % fullpath)
            df_prev = pd.read_csv(fullpath, index_col=0)
            df_full = pd.concat([df_prev, df])\
                        .reset_index()\
                        .drop_duplicates(subset='datetime')\
                        .set_index('datetime')
            df_full.sort_index(axis=0, inplace=True)
            df_full.to_csv(fullpath, index=True, sep=',', encoding='utf-8')
        else:
            self.log.info('Creating %s' % fullpath)
            df.to_csv(fullpath, index=True, sep=',', encoding='utf-8')

    def get_data_from_local(self, filepath, filename):
        df = pd.read_csv(filepath + filename + '.csv')
        df.datetime = [iso8601.parse_date(x) for x in list(df.datetime)]
        df.set_index(['datetime'], inplace=True, drop=False)
        df.sort_index(axis=0, inplace=True)
        return df
