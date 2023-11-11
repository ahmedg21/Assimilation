import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA

# Charger vos données
# Remplacez cela par le chargement de vos propres données
# Exemple fictif :
data = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv', index_col='Date', parse_dates=True)
data = data.dropna()
y = data['Bel Air']

# Diviser vos données en ensembles d'entraînement et de test
train_size = int(len(y) * 0.8)
train, test = y[:train_size], y[train_size:]

# Fit du premier modèle ARIMA
model1 = ARIMA(train, order=(2, 1, 1))  # Remplacez p1, d1, q1 par les ordres appropriés pour votre premier modèle
results1 = model1.fit()
pred1 = results1.get_forecast(steps=len(test))
pred_ci1 = pred1.conf_int()

# Fit du deuxième modèle ARIMA
model2 = ARIMA(train, order=(3, 0, 2))  # Remplacez p2, d2, q2 par les ordres appropriés pour votre deuxième modèle
results2 = model2.fit()
pred2 = results2.get_forecast(steps=len(test))
pred_ci2 = pred2.conf_int()

# Plotting des résultats
plt.figure(figsize=(12, 6))

# Plot des données observées
y.plot(label='Observed', linewidth=2)

# Plot des prédictions du premier modèle
pred1.predicted_mean.plot(label='Model 1 Forecast', linewidth=2)

# Plot des prédictions du deuxième modèle
pred2.predicted_mean.plot(label='Model 2 Forecast', linewidth=2)

# Intervalle de confiance pour le premier modèle
plt.fill_between(pred_ci1.index, pred_ci1.iloc[:, 0], pred_ci1.iloc[:, 1], color='blue', alpha=0.2)

# Intervalle de confiance pour le deuxième modèle
plt.fill_between(pred_ci2.index, pred_ci2.iloc[:, 0], pred_ci2.iloc[:, 1], color='orange', alpha=0.2)

plt.title('Comparison of Two ARIMA Models')
plt.xlabel('Date')
plt.ylabel('Your Y-Axis Label')
plt.legend()
plt.show()
