import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA

# Charger votre série temporelle
# Assurez-vous d'avoir vos données dans un format approprié, par exemple dans un DataFrame avec une colonne 'timestamp' et une colonne 'value'.
# Remplacez les valeurs ci-dessous par vos données réelles.

data = pd.read_csv('votre_fichier.csv')
# Si nécessaire, convertissez la colonne 'timestamp' en index temporel
data['timestamp'] = pd.to_datetime(data['timestamp'])
data.set_index('timestamp', inplace=True)

# Vérifier la stationnarité
def test_stationarity(timeseries):
    # Test de Dickey-Fuller augmenté
    result = adfuller(timeseries, autolag='AIC')
    print("Test de Dickey-Fuller Augmenté :")
    print("Statistique de test :", result[0])
    print("Valeur p :", result[1])
    print("Valeurs critiques :", result[4])
    if result[1] <= 0.05:
        print("La série est stationnaire")
    else:
        print("La série n'est pas stationnaire")

# Afficher la série temporelle
plt.plot(data)
plt.title('Série temporelle')
plt.show()

# Vérifier la stationnarité
test_stationarity(data['value'])

# Différenciation
data_diff = data.diff().dropna()

# Vérifier la stationnarité de la série différenciée
test_stationarity(data_diff['value'])

# Identifier les ordres AR et MA en utilisant les graphiques ACF et PACF
plot_acf(data_diff, lags=20)
plot_pacf(data_diff, lags=20)
plt.show()

# Créer le modèle ARIMA
# Choisissez les ordres AR, I, et MA en fonction des graphiques ACF et PACF
p = 1  # Ordre AR
d = 1  # Ordre de différenciation
q = 1  # Ordre MA
s = 12  # Période saisonnière (par exemple, 12 mois pour des données mensuelles)

# Créer et ajuster le modèle ARIMA
model = ARIMA(data['value'], order=(p, d, q), seasonal_order=(0, 1, 1, s))
results = model.fit()

# Afficher les diagnostics du modèle
print(results.summary())

# Faire des prédictions
forecast_steps = 12  # Nombre d'étapes à prédire
forecast, stderr, conf_int = results.forecast(steps=forecast_steps)

# Afficher les prédictions
plt.plot(data.index, data['value'], label='Données réelles')
plt.plot(pd.date_range(start=data.index[-1], periods=forecast_steps + 1, freq='M')[1:], forecast, label='Prévisions')
plt.fill_between(pd.date_range(start=data.index[-1], periods=forecast_steps + 1, freq='M')[1:], forecast - 1.96 * stderr, forecast + 1.96 * stderr, color='gray', alpha=0.2, label='Intervalles de confiance')
plt.legend()
plt.title('Prévisions avec le modèle ARIMA')
plt.show()
