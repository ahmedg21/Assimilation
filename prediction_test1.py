import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = ''
hote = 'localhost'
base_de_donnees = 'poussiere'

# Établissez une connexion à la base de données MySQL
connexion = mysql.connector.connect(
    user=nom_utilisateur,
    password=mot_de_passe,
    host=hote,
    database=base_de_donnees
)

# Chargez vos données depuis la base de données en utilisant pandas
# Remplacez 'votre_requete_sql' par votre propre requête SQL pour récupérer les données
requete_sql = 'SELECT event, pm25_m FROM moyenne WHERE event >= CURDATE() - INTERVAL 30 DAY'
donnees = pd.read_sql_query(requete_sql, connexion)

# Réglez les ordres ARIMA
p, d, q = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés

# Créez un modèle ARIMA avec les ordres spécifiés
model = sm.tsa.ARIMA(donnees['pm25_m'], order=(p, d, q))

# Ajustez le modèle aux données
model_fit = model.fit()

# Effectuez la prédiction pour le jour suivant (n+1)
date_demain = datetime.now() + timedelta(days=1)
forecast = model_fit.get_forecast(steps=1)

# Récupérez la valeur prédite pour demain
forecasted_value = forecast.predicted_mean.values[0]

print("Prédiction pour demain (n+1):", forecasted_value)
