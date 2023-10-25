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

# Préparer une liste pour stocker les résultats des meilleures combinaisons
best_results = []

# Préparer une liste pour stocker tous les résultats des combinaisons
all_results = []

# Parcourir toutes les combinaisons possibles d'ordre pour p, d et q
p_values = range(0, 5)
d_values = range(0, 2)
q_values = range(0, 5)

for p in p_values:
    for d in d_values:
        for q in q_values:
            try:
                model = sm.tsa.ARIMA(daily_data, order=(p, d, q))
                model_fit = model.fit()
                
                bic = model_fit.bic
                aic = model_fit.aic
                
                all_results.append({
                    'order': (p, d, q),
                    'bic': bic,
                    'aic': aic
                })
                
                if len(best_results) == 0 or bic < best_results[-1]['bic']:
                    best_results.append({
                        'order': (p, d, q),
                        'bic': bic,
                        'aic': aic
                    })
            except:
                continue

# Trouver les meilleures combinaisons pour BIC et AIC
best_bic_combination = min(best_results, key=lambda x: x['bic'])
best_aic_combination = min(best_results, key=lambda x: x['aic'])

print(f"Meilleure combinaison BIC : {best_bic_combination['order']} (BIC : {best_bic_combination['bic']})")
print(f"Meilleure combinaison AIC : {best_aic_combination['order']} (AIC : {best_aic_combination['aic']})")

# Ajuster le modèle ARIMA avec la meilleure combinaison
best_model = sm.tsa.ARIMA(daily_data, order=best_bic_combination['order'])
best_model_fit = best_model.fit()

# Prédictions futures
forecast_steps = 12  # Nombre d'étapes de prévision (toutes les 2 heures pendant 24 heures)
forecast = best_model_fit.forecast(steps=forecast_steps)

# Créer un index pour les dates futures (toutes les 2 heures)
future_dates = pd.date_range(start=daily_data.index[-1], periods=forecast_steps + 1, freq='2H')[1:]

# Créer un DataFrame pour les prédictions futures avec les dates correctes
forecast_df = pd.DataFrame({'pm25': forecast}, index=future_dates)

# Créer un DataFrame à partir de la liste des résultats
results_df = pd.DataFrame(all_results)

# Enregistrer le DataFrame des résultats dans un fichier Excel
results_df.to_excel('resultats_combinaisons2.xlsx', index=False)

# Tracer le graphique des séries temporelles avec prédictions futures
plt.figure(figsize=(10, 6))
plt.plot(daily_data.index, daily_data, label='Données originales')
plt.plot(best_model_fit.fittedvalues.index, best_model_fit.fittedvalues, color='red', label='Valeurs ajustées')
plt.plot(forecast_df.index, forecast_df['pm25'], color='orange', linestyle='dashed', label='Prédictions futures')
plt.title('Séries temporelles de pm25 avec modèle ARIMA et prédictions futures')
plt.xlabel('Date')
plt.ylabel('pm25')
plt.legend()

# Sauvegarder le graphique au format PNG
plt.savefig('resultat_pm25_arima.png')

# Afficher le graphique
plt.show()
