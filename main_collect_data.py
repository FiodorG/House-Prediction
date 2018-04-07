from lib.dataapi import DataAPIFred

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


def detrend_series(df, colname):
    df['dt'] = (df.index - df.index[0]).days
    values = df[[colname, 'dt']].dropna()

    coefficients = np.polyfit(values.dt, values[colname], 1, full=True)
    df[colname + '_trend'] = [coefficients[0][0]*x + coefficients[0][1] for x in df.dt]
    df[colname + '_detrend'] = df[colname] - df[colname + '_trend']

    df.drop(['dt'], axis=1, inplace=True)

    return df


api = DataAPIFred()

requests = [
    'NJRVAC',        # Rental Vacancy Rate for New Jersey
    'NJHVAC',        # Home Vacancy Rate for New Jersey
    'NJSTHPI',       # All-Transactions House Price Index for New Jersey
    'A229RX0',       # Real Disposable Personal Income: Per Capita
    'NJHOWN',        # Homeownership Rate for New Jersey
    'MORTGAGE15US',  # 15-Year Fixed Rate Mortgage Average in the US
    'MSACSR',        # Monthly Supply of Houses in the US
]

date_start = '1/1/1975'
date_end = '1/1/2099'
df = api.query_data(requests, date_start, date_end)

# res = api.search('New Jersey')
# info = api.get_series_info(requests)
# info = [x.title for x in info]


# Detrend NJSTHPI
df = detrend_series(df, 'NJSTHPI')

# Get mortgage rates. These come out on thursdays. So need to align them to
# first of months.
df['MORTGAGE15US'] = df['MORTGAGE15US'].fillna(method='ffill')
df = df[df.index.day == 1]

# Not sure we actually need this
# df['NJSTHPI_detrend_per_disposable_income'] = df['NJSTHPI_detrend'] / df['A229RX0']

df.interpolate(method='time', inplace=True)
#df.dropna(axis='index', how='any', inplace=True)
df = df.apply(np.log).diff(periods=1).dropna(axis='index', how='any')

y_names = ['NJSTHPI_detrend']
x_names = [col for col in df.columns if 'NJSTHPI' not in col]

y = df[y_names]
x = df.drop(list(df.filter(regex='NJSTHPI')), axis=1)

g = sns.pairplot(df, kind="reg", markers="+", x_vars=x_names, y_vars=y_names)
df.plot(subplots=True, figsize=(10, 20), layout=(4, 3))
sns.heatmap(df.corr(), annot=True, center=0, linewidths=.5)
plt.yticks(rotation=0)
plt.xticks(rotation=0)



results = smf.ols('NJSTHPI ~ NJNGSP', data=df).fit()
print(results.summary())

filepath = 'C:\\Users\\gorokf\\Dropbox\\HousePrediction\\data\\FRED\\'
filename = 'NJ'
api.save_data_to_local(df, filepath, filename)
