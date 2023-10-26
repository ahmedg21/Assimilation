import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# Charger les données depuis le fichier CSV
data = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv')

# Supprimer les lignes avec des valeurs de "pm25" supérieures à 150
data = data[data['Bel Air'] <= 150]

# Supprimer les colonnes non nécessaires et formater les données
data = data.dropna()  # Supprimer les lignes avec des valeurs manquantes
data['Date'] = pd.to_datetime(data['date'])  # Convertir la colonne Date en type datetime
data = data.set_index('Date')  # Définir la colonne Date comme index

# Trier l'index dans l'ordre croissant
data = data.sort_index()

# Sélectionner les données à partir du 1er mai 2023
start_date = '2010-01-01'
selected_data = data[start_date:]

# Sélectionner la colonne "pm25"
series_data = selected_data['pm25']

# Régulariser les données avec une fréquence de 15 minutes en utilisant la méthode 'pad'
data1 = series_data.asfreq('D', method='pad')

# Regrouper les données par jour et calculer la moyenne
#daily_data = data_uniforme.resample('D').mean()

# Préparer une liste pour stocker les résultats des meilleures combinaisons
best_results = []

# Préparer une liste pour stocker tous les résultats des combinaisons
all_results = []

# Parcourir toutes les combinaisons possibles d'ordre pour p, d et q
p_values = range(0, 4)
d_values = range(0, 2)
q_values = range(0, 4)

for p in p_values:
    for d in d_values:
        for q in q_values:
            try:
                model = sm.tsa.ARIMA(data1, order=(p, d, q))
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

# Afficher tous les résultats des combinaisons
print("Résultats de toutes les combinaisons possibles :")
for result in all_results:
    print(f"Ordre : {result['order']} | BIC : {result['bic']} | AIC : {result['aic']}")

# Trouver les meilleures combinaisons pour BIC et AIC
best_bic_combination = min(best_results, key=lambda x: x['bic'])
best_aic_combination = min(best_results, key=lambda x: x['aic'])

print(f"\nMeilleure combinaison BIC : {best_bic_combination['order']} (BIC : {best_bic_combination['bic']})")
print(f"Meilleure combinaison AIC : {best_aic_combination['order']} (AIC : {best_aic_combination['aic']})")

# Créer un DataFrame à partir de la liste des résultats
results_df = pd.DataFrame(all_results)

# Enregistrer le DataFrame dans un fichier Excel
results_df.to_excel('resultats_combinaisons.xlsx', index=False)

# Tracer le graphique des séries temporelles
plt.figure(figsize=(10, 6))
plt.plot(data1.index, data1['Bel Air'], label='Données originales')
plt.plot(model_fit.fittedvalues.index, model_fit.fittedvalues, color='red', label='Valeurs ajustées')
plt.title('Séries temporelles de pm25 avec modèle ARIMA')
plt.xlabel('Date')
plt.ylabel('pm25')
plt.legend()

# Sauvegarder le graphique au format PNG
plt.savefig('resultat_pm25_arima.png')

# Afficher le graphique
plt.show()
