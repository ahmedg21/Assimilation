import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
from itertools import product
from sklearn.metrics import mean_squared_error

# Charger les données (remplacez 'votre_fichier.csv' par le nom de votre fichier)
data = pd.read_csv('votre_fichier.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Diviser les données en ensembles d'entraînement et de test
split_index = int(len(data) * 0.8)  # 80% pour l'entraînement, 20% pour le test
data_train = data.iloc[:split_index]
data_test = data.iloc[split_index:]

# Paramètres pour la recherche par grille
p_values = range(0, 3)
d_values = [0, 1]
q_values = range(0, 3)
best_rmse = float("inf")
best_order = None

# Recherche par grille pour trouver les meilleurs ordres
for p, d, q in product(p_values, d_values, q_values):
    try:
        model = ARIMA(data_train, order=(p, d, q))
        results = model.fit()
        forecast, stderr, conf_int = results.forecast(steps=len(data_test))
        rmse = np.sqrt(mean_squared_error(data_test['Valeur'], forecast))
        if rmse < best_rmse:
            best_rmse = rmse
            best_order = (p, d, q)
    except:
        continue

print("Best RMSE:", best_rmse)
print("Best Order:", best_order)

# Utiliser les meilleurs ordres pour ajuster le modèle ARIMA complet
model = ARIMA(data, order=best_order)
results = model.fit()

# Prévisions pour l'ensemble complet
forecast, stderr, conf_int = results.forecast(steps=len(data))

# Tracer les prévisions et les valeurs réelles
plt.figure(figsize=(10, 6))
plt.plot(data, label='Données réelles')
plt.plot(data.index, forecast, label='Prévisions')
plt.fill_between(data.index, forecast - stderr, forecast + stderr, color='gray', alpha=0.2)
plt.title('Prévisions ARIMA')
plt.xlabel('Date')
plt.ylabel('Valeur')
plt.legend()
plt.show()
