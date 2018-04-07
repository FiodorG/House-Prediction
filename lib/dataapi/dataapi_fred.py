from .dataapi import DataAPIInterface

import fredapi
import pandas as pd


class DataAPIFred(DataAPIInterface):

    def __init__(self):
        """
        API Github: https://github.com/mortada/fredapi
        Data Source: https://research.stlouisfed.org/
        """
        DataAPIInterface.__init__(self)

        self.key = '4ee85758812cd4eccda171cd90572fb2'
        self.fred = fredapi.Fred(api_key=self.key)

        self.log.info('Starting FRED API with key %s' % self.key)

    def query_data(self, requests, date_start, date_end):
        """
        Every observation can have three dates associated with it:

        date: the date the value is for
        realtime_start: the first date the value is valid
        realitime_end: the last date the value is valid
        """
        dfs = []
        for request in requests:
            df = self.fred.get_series(request, date_start, date_end).to_frame()
            df.columns = [request]
            df.index.names = ['datetime']
            dfs.append(df)
        return pd.concat(dfs, axis=1)

    def search(self, request):
        """
        request: request to search for in FRED database
        """

        return self.fred.search(request)

    def get_series_info(self, requests):
        """
        requests: requests to search for in FRED database
        """
        infos = []
        for request in requests:
            infos.append(self.fred.get_series_info(request))

        return infos
