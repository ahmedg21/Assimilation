import pandas as pd
import matplotlib.pyplot as plt


excel_path = 'C:/Users/USER6PC/3D Objects/ASSIMILATION/data_AD.xlsx'

# Read the Excel file and parse dates
series = pd.read_excel(excel_path)

# Remove missing values and zeros
series = series.dropna()  # Remove NaN values
series = series[series != 0]  # Remove zero values

print(series.head())

