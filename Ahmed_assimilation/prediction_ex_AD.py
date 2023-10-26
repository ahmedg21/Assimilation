import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import json
import time
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr

def run_script():
    excel_file = 'C:/Users/DELL/Desktop/python/data_AD.xlsx'
    data_from_csv = pd.read_excel(excel_file, parse_dates=['Date'], index_col='Date')
    data_from_csv['pm25'] = pd.to_numeric(data_from_csv['Bel Air'], errors='coerce')
    data_from_csv.dropna(subset=['pm25'], inplace=True)
    
    model = sm.tsa.ARIMA(data_from_csv['pm25'], order=(3, 0, 2))
    results = model.fit()
    
    num_days = 7
    freq_daily = 'D'
    index_forecast = pd.date_range(start=data_from_csv.index[-1], periods=num_days, freq=freq_daily)
    
    forecast = results.get_forecast(steps=num_days)
    forecasted_values = forecast.predicted_mean
    confidence_intervals = forecast.conf_int()
    
    index_forecast_str = index_forecast.strftime('%Y-%m-%d %H:%M:%S')
    
    predictions_dict = {
        'datetime': index_forecast_str.tolist(),
        'pm25_predicted': forecasted_values.tolist(),
        'pm25_lower_conf': confidence_intervals.iloc[:, 0].tolist(),
        'pm25_upper_conf': confidence_intervals.iloc[:, 1].tolist()
    }
    
    output_directory = 'C:/Users/DELL/Desktop/python/'
    output_filename = 'predictions_Belair.json'
    output_path = os.path.join(output_directory, output_filename)
    
    with open(output_path, 'w') as f:
        json.dump(predictions_dict, f)
    
    plt.figure(figsize=(10, 6))
    plt.plot(data_from_csv.index, data_from_csv['pm25'], label='Données réelles')
    plt.plot(index_forecast, forecasted_values, label='Prévisions')
    plt.fill_between(index_forecast, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1], color='gray', alpha=0.3, label='Intervalles de confiance')
    plt.legend()
    plt.title('Données réelles, prévisions et intervalles de confiance')
    plt.xlabel('Date')
    plt.ylabel('PM2.5')
    plt.show()
    
    plt.figure(figsize=(10, 6))
    plt.plot(index_forecast, forecasted_values, label='Prévisions')
    plt.fill_between(index_forecast, confidence_intervals.iloc[:, 0], confidence_intervals.iloc[:, 1], color='gray', alpha=0.3, label='Intervalles de confiance')
    plt.legend()
    plt.title('Prévisions et intervalles de confiance')
    plt.xlabel('Date')
    plt.ylabel('PM2.5')
    plt.show()
    
    correlation_coefficient, _ = pearsonr(data_from_csv['pm25'], forecasted_values)
    rmse = np.sqrt(mean_squared_error(data_from_csv['pm25'], forecasted_values))
    
    print(f"Coefficient de corrélation : {correlation_coefficient}")
    print(f"RMSE : {rmse}")

while True:
    run_script()
    time.sleep(86400)
