import pandas as pd
import matplotlib.pyplot as plt

def parser(x):
    return pd.to_datetime('201' + x, format='%Y-%m')

# Read the Excel file and parse dates
excel_path = 'C:/Users/USER6PC/3D Objects/ASSIMILATION/data.xlsx'
series = pd.read_excel(excel_path, header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)

# Remove missing values and zeros
series = series.dropna()  # Remove NaN values
series = series[series != 0]  # Remove zero values

print(series.head())
series.plot()
plt.show()
