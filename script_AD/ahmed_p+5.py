import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import numpy as np
import matplotlib.pyplot as plt

# Définition d'une fonction d'analyseur pour convertir les chaînes de date en objets datetime
def analyseur(x):
    return pd.to_datetime(x)

# Chargement du jeu de données à partir d'un fichier CSV
series = pd.read_csv('C:/Users/DELL/Documents/ASSIMILATION/data.csv', header=0, index_col=0, parse_dates=True, date_parser=analyseur)

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

# Initialisation d'un buffer P + 5 pour stocker les valeurs prédites
buffer_plus_five = []

# Initialisation d'une liste pour stocker les observations correspondantes (P + 5)
observed_plus_five = []

# Boucle de validation pas à pas
for t in range(len(test) - 4):
    # Création d'un modèle ARIMA avec un ordre de (3, 0, 2)
    model = ARIMA(train, order=(3, 0, 2))
    
    # Ajustement du modèle aux données historiques
    model_fit = model.fit()
    
    # Prévision des cinq prochaines valeurs (P + 5)
    yhat = model_fit.forecast(steps=6)[1:]  # Prévision des deuxième à sixième valeurs (P + 5)
    
    # Stockage des valeurs prédites
    buffer_plus_five.extend(yhat)
    
    # Stockage des valeurs réelles correspondantes (P + 5)
    observed_plus_five.extend(test[t:t+5])
    
    # Ajout des valeurs réelles aux données d'entraînement pour les prochaines itérations
    train = np.append(train, test[t:t+4])

# Calcul du coefficient de corrélation entre les valeurs prédites et observées (P + 5)
correlation = np.corrcoef(observed_plus_five, buffer_plus_five)[0, 1]
print('Coefficient de corrélation (P + 5) : %.3f' % correlation)

# Calcul de l'erreur quadratique moyenne (RMSE) entre les valeurs prédites et observées (P + 5)
rmse = np.sqrt(mean_squared_error(observed_plus_five, buffer_plus_five))
print('RMSE (P + 5) : %.3f' % rmse)

# Création d'un DataFrame pour les prédictions P + 5 et les observations correspondantes
results_df = pd.DataFrame({'Observé (P + 5)': observed_plus_five, 'Prédit (P + 5)': buffer_plus_five})

# Sauvegarde du DataFrame dans un fichier CSV
results_df.to_csv('predictions_p_plus_five.csv', index=False)

# Tracé des valeurs observées (P + 5) et prédites (P + 5)
plt.plot(observed_plus_five, label='Observé (P + 5)')
plt.plot(buffer_plus_five, color='red', label='Prédit (P + 5)')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Valeur')
plt.title('Prédictions P + 5 vs Observations P + 5')
plt.show()

# Affichage d'un message de confirmation
print("Prédictions P + 5 enregistrées dans 'predictions_p_plus_five.csv'")
