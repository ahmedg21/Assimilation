import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = ''
hote = 'localhost'
base_de_donnees = 'pollution'

# Créez une connexion à la base de données MySQL en utilisant SQLAlchemy
connexion_uri = f"mysql+mysqlconnector://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}"
engine = create_engine(connexion_uri)

# Chargez vos données depuis la base de données en utilisant pandas
# Remplacez 'votre_requete_sql' par votre propre requête SQL pour récupérer les données
requete_sql = 'SELECT event, pm25_m FROM moyenne WHERE event >= CURDATE() - INTERVAL 30 DAY'
donnees = pd.read_sql_query(requete_sql, engine)

# Réglez les ordres ARIMA
p, d, q = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés

# Créez un modèle ARIMA avec les ordres spécifiés
model = sm.tsa.ARIMA(donnees['pm25_m'], order=(p, d, q))

# Ajustez le modèle aux données
model_fit = model.fit()

# Effectuez la prédiction pour le jour même (n)
date_n = datetime.now()
forecast_n = model_fit.get_forecast(steps=1)

# Effectuez la prédiction pour le jour suivant (n+1)
date_demain = date_n + timedelta(days=1)
forecast_n1 = model_fit.get_forecast(steps=1)

# Effectuez la prédiction pour le jour après demain (n+2)
date_apres_demain = date_demain + timedelta(days=1)
forecast_n2 = model_fit.get_forecast(steps=2)

# Récupérez les valeurs prédites pour le jour même (n), demain (n+1) et le jour après demain (n+2)
forecasted_value_n = forecast_n.predicted_mean.values[0]
forecasted_value_n1 = forecast_n1.predicted_mean.values[0]
forecasted_value_n2 = forecast_n2.predicted_mean.values[1]

print("Prédiction pour le jour même (n):", forecasted_value_n)
print("Prédiction pour demain (n+1):", forecasted_value_n1)
print("Prédiction pour le jour après demain (n+2):", forecasted_value_n2)
