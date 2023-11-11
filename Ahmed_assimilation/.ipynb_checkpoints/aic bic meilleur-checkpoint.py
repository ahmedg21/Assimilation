import pandas as pd
import numpy as np
import statsmodels.api as sm

# Charger les données à partir du fichier CSV
data = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv', index_col='Date')
# Assurez-vous que 'votre_colonne_temporelle' est le nom de la colonne temporelle dans votre fichier CSV
data = data.dropna()
data1 = data['Bel Air']  # Utilisation de la colonne 'Bel Air' comme exemple, veuillez ajuster selon vos besoins

# Définir une plage de valeurs pour les ordres p, d et q
p_values = range(0, 5)  # Remplacez 3 par une valeur appropriée selon votre cas
d_values = range(0, 2)  # Remplacez 2 par une valeur appropriée selon votre cas
q_values = range(0, 5)  # Remplacez 3 par une valeur appropriée selon votre cas

# Liste pour stocker les résultats des modèles et les critères d'information
results = []
aic_values = []
bic_values = []

# Boucles pour tester différentes combinaisons d'ordres p, d et q
for p in p_values:
    for d in d_values:
        for q in q_values:
            try:
                # Ajuster le modèle ARIMA
                model = sm.tsa.ARIMA(data1, order=(p, d, q))  # Utilisez data1 ici au lieu de data
                fit_model = model.fit(disp=0)
                
                # Calculer AIC et BIC
                aic = fit_model.aic
                bic = fit_model.bic
                
                # Stocker les résultats
                results.append((p, d, q))
                aic_values.append(aic)
                bic_values.append(bic)
                
            except:
                continue

# Trouver l'index du modèle avec le plus petit AIC
best_aic_index = np.argmin(aic_values)
best_aic_model = results[best_aic_index]
best_aic = aic_values[best_aic_index]

# Trouver l'index du modèle avec le plus petit BIC
best_bic_index = np.argmin(bic_values)
best_bic_model = results[best_bic_index]
best_bic = bic_values[best_bic_index]

print("Meilleur modèle ARIMA basé sur AIC : Order({}, {}, {}) - AIC: {}".format(best_aic_model[0], best_aic_model[1], best_aic_model[2], best_aic))
print("Meilleur modèle ARIMA basé sur BIC : Order({}, {}, {}) - BIC: {}".format(best_bic_model[0], best_bic_model[1], best_bic_model[2], best_bic))

