import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from itertools import product
import warnings
import matplotlib.pyplot as plt

# Charger vos données dans un DataFrame pandas
data = pd.read_csv('C:/Users/NZO BUSINESS/Documents/Assimilation/data.csv',  header=0, index_col=0, parse_dates=True, date_parser=parser)
# Assurez-vous que la colonne temporelle est correctement définie comme index

# Supprimer les valeurs manquantes si nécessaire
data = data.dropna()
data.index = data.index.to_period('D')
data1 = data['Bel Air']
# Diviser les données en ensembles d'entraînement et de test (80% - 20%)
n_total = len(data1)
n_test = int(0.2 * n_total)
n_train = n_total - n_test

train_data = data1.iloc[:n_train]
test_data = data1.iloc[n_train:]

# Paramètres max pour p, d et q
max_p = 3
max_d = 1
max_q = 3

# Créer une liste de combinaisons possibles de p, d et q
p_values = range(0, max_p + 1)
d_values = range(0, max_d + 1)
q_values = range(0, max_q + 1)
combinations = list(product(p_values, d_values, q_values))

best_aic = float("inf")
best_bic = float("inf")
best_order = None
best_order_bic = None

# Boucle à travers toutes les combinaisons de p, d et q
for order in combinations:
    p, d, q = order
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            model = ARIMA(train_data, order=order)
            results = model.fit()
            aic = results.aic
            bic = results.bic
            if aic < best_aic:
                best_aic = aic
                best_order = order
            if bic < best_bic:
                best_bic = bic
                best_order_bic = order
    except:
        continue

print("Best AIC Order:", best_order, "AIC:", best_aic)
print("Best BIC Order:", best_order_bic, "BIC:", best_bic)

# Ajuster le meilleur modèle sur l'ensemble d'entraînement complet
best_model = ARIMA(train_data, order=best_order)
best_results = best_model.fit()

# Prédictions sur l'ensemble de test
predictions = best_results.predict(start=test_data.index[0], end=test_data.index[-1])

# Tracer les prédictions et les données réelles
plt.figure(figsize=(10, 6))
plt.plot(train_data.index, train_data, label='Données d\'entraînement', color='blue')
plt.plot(test_data.index, test_data, label='Données de test', color='orange')
plt.plot(test_data.index, predictions, label='Prédictions', color='green')

# Personnaliser le graphe
plt.xlabel('Date')
plt.ylabel('PM2.5')
plt.title('Prédictions du modèle ARIMA')
plt.legend()
plt.xticks(rotation=45)  # Rotation des étiquettes x
plt.tight_layout()

# Afficher le graphe
plt.show()
