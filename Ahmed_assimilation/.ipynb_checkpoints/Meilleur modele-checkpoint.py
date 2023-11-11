import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Charger les données à partir du fichier CSV
data = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv', index_col='Date')
# Assurez-vous que 'votre_colonne_temporelle' est le nom de la colonne temporelle dans votre fichier CSV
data=data.dropna()
data1=data['Bel Air']
# Définir le nombre de splits pour la validation croisée
n_splits = 5
tscv = TimeSeriesSplit(n_splits=n_splits)

# Définir les valeurs possibles pour p, d, et q
p_values = range(5)  # Remplacez 3 par une valeur appropriée pour votre cas
d_values = range(2)  # Remplacez 3 par une valeur appropriée pour votre cas
q_values = range(5)  # Remplacez 3 par une valeur appropriée pour votre cas

# Initialiser les métriques
best_mae = float("inf")
best_mse = float("inf")
best_rmse = float("inf")
best_r2 = float("-inf")
best_order = None

# Boucle sur différentes combinaisons d'ordres p, d, et q
for p in p_values:
    for d in d_values:
        for q in q_values:
            mae_scores = []
            mse_scores = []
            rmse_scores = []
            r2_scores = []

            # Effectuer la validation croisée pour chaque combinaison d'ordres
            for train_index, test_index in tscv.split(data1):
                train, test = data1.iloc[train_index], data1.iloc[test_index]
                try:
                    # Ajuster le modèle ARIMA
                    model = ARIMA(train, order=(p, d, q))
                    model_fit = model.fit()

                    # Faire des prédictions
                    predictions = model_fit.forecast(steps=len(test))

                    # Calculer les métriques d'évaluation
                    mae = mean_absolute_error(test, predictions)
                    mse = mean_squared_error(test, predictions)
                    rmse = np.sqrt(mse)
                    r2 = r2_score(test, predictions)

                    # Ajouter les scores aux listes correspondantes
                    mae_scores.append(mae)
                    mse_scores.append(mse)
                    rmse_scores.append(rmse)
                    r2_scores.append(r2)
                except:
                    # Ignorer les erreurs lors de l'ajustement du modèle
                    pass

            # Calculer les moyennes des métriques sur les plis de validation croisée
            avg_mae = np.mean(mae_scores)
            avg_mse = np.mean(mse_scores)
            avg_rmse = np.mean(rmse_scores)
            avg_r2 = np.mean(r2_scores)

            # Mettre à jour les ordres optimaux si les métriques sont meilleures
            if avg_mae < best_mae and avg_mse < best_mse and avg_rmse < best_rmse and avg_r2 > best_r2:
                best_mae = avg_mae
                best_mse = avg_mse
                best_rmse = avg_rmse
                best_r2 = avg_r2
                best_order = (p, d, q)

print("Meilleurs ordres (p, d, q) :", best_order)
print("MAE :", best_mae)
print("MSE :", best_mse)
print("RMSE :", best_rmse)
print("R^2 :", best_r2)
