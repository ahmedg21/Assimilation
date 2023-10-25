from matplotlib import pyplot
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

def evaluate_arima_model(X, arima_order):
    train_size = int(len(X) * 0.80)
    train, test = X[0:train_size], X[train_size:]
    history = [x for x in train]
    
    predictions = []  # Use an empty list instead of list()
    for t in range(len(test)):
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit()
        yhat = model_fit.forecast()[0]
        predictions.append(yhat)
        history.append(test[t])
        
    rmse = sqrt(mean_squared_error(test, predictions))
    return rmse

def evaluate_models(dataset, p_values, d_values, q_values):
    dataset = dataset.astype('float32')
    best_score, best_cfg = float("inf"), None
    
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p, d, q)
                try:
                    rmse = evaluate_arima_model(dataset, order)
                    if rmse < best_score:
                        best_score, best_cfg = rmse, order
                    print('ARIMA%s RMSE=%.3f' % (order, rmse))
                except:
                    continue
                    
    print('Best ARIMA%s RMSE=%.3f' % (best_cfg, best_score))

# Load dataset
def parser(x):
    return pd.to_datetime(x)

# Load the dataset and preprocess
series = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv', header=0, index_col=0, parse_dates=True, date_parser=parser)
series = series.dropna()
series.index = series.index.to_period('D')
X = series['Bel Air'].values

# Define parameter search space
p_values = [0, 1, 2, 3, 4, 5]
d_values = range(0, 3)
q_values = range(0, 5)

# Evaluate models
warnings.filterwarnings("ignore")
evaluate_models(X, p_values, d_values, q_values)
