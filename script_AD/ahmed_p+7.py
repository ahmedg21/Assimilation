import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import numpy as np
import matplotlib.pyplot as plt

# Définition d'une fonction d'analyseur pour convertir les chaînes de date en objets datetime
def analyseur(x):
    return pd.to_datetime(x)

# Chargement du jeu de données à partir d'un fichier CSV
series = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv', header=0, index_col=0, parse_dates=True, date_parser=analyseur)

# Suppression des lignes avec des valeurs manquantes (NaN)
series = series.dropna()

# Conversion de l'index en un Index de périodes avec une fréquence quotidienne
series.index = series.index.to_period('D')

# Extraction des valeurs de la colonne 'Bel Air' en tant que données de séries temporelles
X = series['Bel Air'].values

# Calcul de la taille pour l'ensemble d'entraînement (80 % des données)
size = int(len(X) * 0.80)

# Séparation des données en ensembles d'entraînement et de test
train, test = X[0:size], X[size:len(X)]

# Initialisation d'un buffer P + 7 pour stocker les valeurs prédites
buffer_plus_seven = []

# Initialisation d'une liste pour stocker les observations correspondantes (P + 7)
observed_plus_seven = []

# Boucle de validation pas à pas
for t in range(len(test) - 6):
    # Création d'un modèle ARIMA avec un ordre de (3, 0, 2)
    model = ARIMA(train, order=(2, 1, 1))
    
    # Ajustement du modèle aux données historiques
    model_fit = model.fit()
    
    # Prévision des sept prochaines valeurs (P + 7)
    yhat = model_fit.forecast(steps=8)[1:]  # Prévision des deuxième à huitième valeurs (P + 7)
    
    # Stockage des valeurs prédites
    buffer_plus_seven.extend(yhat)
    
    # Stockage des valeurs réelles correspondantes (P + 7)
    observed_plus_seven.extend(test[t:t+7])
    
    # Ajout des valeurs réelles aux données d'entraînement pour les prochaines itérations
    train = np.append(train, test[t:t+6])

# Calcul du coefficient de corrélation entre les valeurs prédites et observées (P + 7)
correlation = np.corrcoef(observed_plus_seven, buffer_plus_seven)[0, 1]
print('Coefficient de corrélation (P + 7) : %.3f' % correlation)

# Calcul de l'erreur quadratique moyenne (RMSE) entre les valeurs prédites et observées (P + 7)
rmse = np.sqrt(mean_squared_error(observed_plus_seven, buffer_plus_seven))
print('RMSE (P + 7) : %.3f' % rmse)

# Création d'un DataFrame pour les prédictions P + 7 et les observations correspondantes
results_df = pd.DataFrame({'Observé (P + 7)': observed_plus_seven, 'Prédit (P + 7)': buffer_plus_seven})

# Sauvegarde du DataFrame dans un fichier CSV
results_df.to_csv('predictions_p_plus_seven_2_1_1.csv', index=False)

# Tracé des valeurs observées (P + 7) et prédites (P + 7)
plt.plot(observed_plus_seven, label='Observé (P + 7)')
plt.plot(buffer_plus_seven, color='red', label='Prédit (P + 7)')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Valeur')
plt.title('Prédictions P + 7 vs Observations P + 7')
plt.show()

# Affichage d'un message de confirmation
print("Prédictions P + 7 enregistrées dans 'predictions_p_plus_seven_2_1_1.csv'")
