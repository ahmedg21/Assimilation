import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Charger les données depuis le fichier CSV
data = pd.read_csv('C:/Users/DELL/Documents/Campagne_Dakar_Pollution/data.csv')

# Supprimer les lignes avec des valeurs de "pm25" supérieures à 150
data = data[data['pm25'] <= 150]

# Supprimer les colonnes non nécessaires et formater les données
data = data.dropna()  # Supprimer les lignes avec des valeurs manquantes
data['Date'] = pd.to_datetime(data['event'])  # Convertir la colonne Date en type datetime
data = data.set_index('Date')  # Définir la colonne Date comme index

# Trier l'index dans l'ordre croissant
data = data.sort_index()

# Sélectionner les données à partir du 1er mai 2023
start_date = '2023-05-01 00:00:00'
selected_data = data[start_date:]

# Sélectionner la colonne "pm25"
series_data = selected_data['pm25']

# Régulariser les données avec une fréquence de 15 minutes en utilisant la méthode 'pad'
data_uniforme = series_data.asfreq('15T', method='pad')

# Regrouper les données par jour et calculer la moyenne
daily_data = data_uniforme.resample('D').mean()

# Prédictions ARIMA avec les données journalières
model = sm.tsa.ARIMA(daily_data, order=(1, 0, 3))
model_fit = model.fit()

print(model_fit.summary())

# Effectuer des prédictions sur le reste des données
forecast = model_fit.predict(start=1, end=len(daily_data) - 1)

# Créer un DataFrame avec les prédictions et la colonne 'pm25'
predictions_data = pd.DataFrame({'pm25': forecast}, index=daily_data.index[1:])

# Appliquer une moyenne mobile (lissage) aux données observées et aux prédictions
window_size = 7  # Taille de la fenêtre pour la moyenne mobile
smoothed_daily_data = daily_data.rolling(window=window_size).mean()
smoothed_predictions_data = predictions_data.rolling(window=window_size).mean()

# Afficher les courbes lissées
plt.figure(figsize=(12, 6))
plt.plot(daily_data.index, smoothed_daily_data, color='blue', label='Données observées (lissées)')
plt.plot(predictions_data.index, smoothed_predictions_data, color='red', label='Prédictions (lissées)')
plt.legend(loc='best')

plt.xticks(rotation=45)  # Rotation de 45 degrés pour les étiquettes d'axe x
plt.xlabel('Date')
plt.ylabel('Valeur de pm25')
plt.title('Prédictions avec le modèle ARIMA (utilisant les données journalières)')
plt.tight_layout()

plt.show()
