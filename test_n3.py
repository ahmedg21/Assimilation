import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = '150421Ah'
hote = 'localhost'
base_de_donnees = 'pollution'

# Créez une connexion à la base de données MySQL en utilisant SQLAlchemy
connexion_uri = f"mysql+mysqlconnector://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}"
engine = create_engine(connexion_uri)

# Chargez vos données depuis la base de données en utilisant pandas
# Remplacez 'votre_requete_sql' par votre propre requête SQL pour récupérer les données
requete_sql = "SELECT event, pm25_m, pm10_m FROM data_j WHERE DATE(event) < CURDATE()"
donnees = pd.read_sql_query(requete_sql, engine)

# Réglez les ordres ARIMA pour PM2.5 et PM10
p_pm25, d_pm25, q_pm25 = 1, 0, 3  # Ordres ARIMA pour PM2.5
p_pm10, d_pm10, q_pm10 = 1, 0, 3  # Ordres ARIMA pour PM10

# Créez un modèle ARIMA pour PM2.5 avec les ordres spécifiés
model_pm25 = sm.tsa.ARIMA(donnees['pm25_m'], order=(p_pm25, d_pm25, q_pm25))
# Créez un modèle ARIMA pour PM10 avec les ordres spécifiés
model_pm10 = sm.tsa.ARIMA(donnees['pm10_m'], order=(p_pm10, d_pm10, q_pm10))

# Ajustez les modèles aux données
model_fit_pm25 = model_pm25.fit()
model_fit_pm10 = model_pm10.fit()

# Obtenez l'heure actuelle
heure_actuelle = datetime.now()
print("Heure actuelle:", heure_actuelle)

# Effectuez la prédiction pour le jour même (n) pour PM2.5
date_n = heure_actuelle
forecast_n_pm25 = model_fit_pm25.get_forecast(steps=1)
forecasted_value_n_pm25 = forecast_n_pm25.predicted_mean.values[0]
print("Prédiction PM2.5 pour le jour même (n) - Date:", date_n)
print("Prédiction PM2.5 pour le jour même (n) - Valeur:", forecasted_value_n_pm25)

# Effectuez la prédiction pour le jour même (n) pour PM10
forecast_n_pm10 = model_fit_pm10.get_forecast(steps=1)
forecasted_value_n_pm10 = forecast_n_pm10.predicted_mean.values[0]
print("Prédiction PM10 pour le jour même (n) - Date:", date_n)
print("Prédiction PM10 pour le jour même (n) - Valeur:", forecasted_value_n_pm10)

# Effectuez la prédiction pour le jour suivant (n+1) pour PM2.5
date_demain = date_n + timedelta(days=1)
forecast_n1_pm25 = model_fit_pm25.get_forecast(steps=1)
forecasted_value_n1_pm25 = forecast_n1_pm25.predicted_mean.values[0]
print("Prédiction PM2.5 pour demain (n+1) - Date:", date_demain)
print("Prédiction PM2.5 pour demain (n+1) - Valeur:", forecasted_value_n1_pm25)

# Effectuez la prédiction pour le jour suivant (n+1) pour PM10
forecast_n1_pm10 = model_fit_pm10.get_forecast(steps=1)
forecasted_value_n1_pm10 = forecast_n1_pm10.predicted_mean.values[0]
print("Prédiction PM10 pour demain (n+1) - Date:", date_demain)
print("Prédiction PM10 pour demain (n+1) - Valeur:", forecasted_value_n1_pm10)

# Effectuez la prédiction pour le jour après demain (n+2) pour PM2.5
date_apres_demain = date_demain + timedelta(days=1)
forecast_n2_pm25 = model_fit_pm25.get_forecast(steps=2)
forecasted_value_n2_pm25 = forecast_n2_pm25.predicted_mean.values[1]
print("Prédiction PM2.5 pour le jour après-demain (n+2) - Date:", date_apres_demain)
print("Prédiction PM2.5 pour le jour après-demain (n+2) - Valeur:", forecasted_value_n2_pm25)

# Effectuez la prédiction pour le jour après demain (n+2) pour PM10
forecast_n2_pm10 = model_fit_pm10.get_forecast(steps=2)
forecasted_value_n2_pm10 = forecast_n2_pm10.predicted_mean.values[1]
print("Prédiction PM10 pour le jour après-demain (n+2) - Date:", date_apres_demain)
print("Prédiction PM10 pour le jour après-demain (n+2) - Valeur:", forecasted_value_n2_pm10)
