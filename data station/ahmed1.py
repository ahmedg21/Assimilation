import pandas as pd
import numpy as np
import statsmodels.api as sm
from itertools import product
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

# Afficher le graphique avec les jours en abscisses et la série temporelle "pm25"
plt.figure(figsize=(12, 5))
data_uniforme.plot(label='Données originales', linewidth=0.5)
daily_data.plot(label='Moyenne journalière', linewidth=2)

plt.xlabel('Date')
plt.ylabel('Valeur de pm25')
plt.title('Série temporelle et moyenne journalière de pm25')
plt.legend()

# Personnalisation de l'affichage des abscisses (jours de la semaine)
#plt.gca().xaxis.set_major_locator(plt.MultipleLocator(base=1))  # Afficher tous les jours

plt.xticks(rotation=45)  # Inclinaison des étiquettes pour une meilleure lisibilité
plt.tight_layout()  # Ajustement automatique des espaces

# Prédictions ARIMA avec les données journalières
model = sm.tsa.ARIMA(daily_data, order=(0, 1, 1))
model_fit = model.fit()

print(model_fit.summary())

# Effectuer des prédictions sur le reste des données
forecast = model_fit.predict(start=1, end=len(daily_data) - 1)

# Créer un DataFrame avec les prédictions et la colonne 'pm25'
predictions_data = pd.DataFrame({'pm25': forecast}, index=daily_data.index[1:])

# Calculer la différence entre les observations réelles et les prédictions
difference = daily_data.iloc[1:] - predictions_data

# Ajouter la colonne de différence au DataFrame predictions_data
predictions_data['Difference'] = difference

# Enregistrer les résultats dans un fichier CSV
results_csv_path = 'predictions_results.csv'
predictions_data.to_csv(results_csv_path)

# Afficher les prédictions
plt.figure(figsize=(12, 6))
plt.plot(daily_data.index, daily_data.values, color='blue', label='Données observées')
plt.plot(predictions_data.index, predictions_data['pm25'], color='red', label='Prédictions')
plt.legend(loc='best')

plt.xticks(rotation=45)  # Rotation de 45 degrés pour les étiquettes d'axe x
plt.title('Prédictions avec le modèle ARIMA (utilisant les données journalières)')
plt.tight_layout()

print(predictions_data)
plt.show()
