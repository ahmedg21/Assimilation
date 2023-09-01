import pandas as pd
import matplotlib.pyplot as plt
from pandas import datetime
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot

def parser(x):
    return pd.to_datetime(x)

series = pd.read_csv('C:/Users/USER6PC/3D Objects/ASSIMILATION/data.csv', header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
series = series.dropna()
print(series.head())
serie = series["Bel Air"]
serie.plot()
plt.show()
autocorrelation_plot(series)
pyplot.show()



