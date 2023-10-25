import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Charger les données à partir du fichier Excel
excel_file = 'data_AD.xlsx'  # Remplacez par le chemin approprié
df = pd.read_excel(excel_file)
df = df.dropna()

# Convertir la colonne Date en type datetime et définir comme index
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')

# Remplir les valeurs manquantes avec la méthode 'pad' (remplissage vers l'avant)
data_uniforme = df.asfreq('D', method='pad')

# Agréger les données en moyennes mensuelles
df_monthly_mean = data_uniforme.resample('M').mean()

# Diviser les données en train_data
train_data = df_monthly_mean['Bel Air'][:-15]

best_rmse = float('inf')
best_r2 = -float('inf')
best_order = None

# Essayer différentes combinaisons de paramètres ARIMA
for p in range(3):
    for d in range(2):
        for q in range(3):
            try:
                model = ARIMA(train_data, order=(p, d, q))
                fitted_model = model.fit()

                # Prédictions sur l'ensemble de test
                test_data = df_monthly_mean['Bel Air'][-15:]
                predictions = fitted_model.forecast(steps=len(test_data))
                
                rmse = np.sqrt(mean_squared_error(test_data, predictions))
                r2 = r2_score(test_data, predictions)

                if rmse < best_rmse and r2 > best_r2:
                    best_rmse = rmse
                    best_r2 = r2
                    best_order = (p, d, q)

            except:
                continue

print("Best RMSE:", best_rmse)
print("Best R²:", best_r2)
print("Best ARIMA Order:", best_order)

# Entraîner le modèle ARIMA avec les meilleurs paramètres sur l'ensemble complet des données d'entraînement
final_model = ARIMA(df_monthly_mean['Bel Air'], order=best_order)
final_fitted_model = final_model.fit()

# Faire des prédictions futures avec le modèle final
future_steps = 10
future_predictions = final_fitted_model.forecast(steps=future_steps)

# Créer un index pour les prédictions futures
future_index = pd.date_range(start=df_monthly_mean.index[-1], periods=future_steps+1, freq='M')[1:]

# Créer un DataFrame pour les prédictions futures
future_predictions_df = pd.DataFrame(index=future_index, data=future_predictions, columns=['future_predictions'])

# Joindre les prédictions futures au DataFrame original 'df_monthly_mean'
combined_data = pd.concat([df_monthly_mean, future_predictions_df])

# Tracer les courbes
plt.figure(figsize=(12, 6))
plt.plot(combined_data.index, combined_data['Bel Air'], label='Valeurs réelles')
plt.plot(test_data.index, predictions, label='Prédictions sur l\'ensemble de test', color='orange')
plt.plot(future_predictions_df.index, future_predictions_df['future_predictions'], label='Prédictions futures', color='green')

plt.title('Prévisions ARIMA pour Bel Air')
plt.xlabel('Date')
plt.ylabel('Valeur')
plt.legend()
plt.show()
