import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

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
requete_sql = "SELECT event, pm25, pm10 FROM data"
donnees = pd.read_sql_query(requete_sql, engine)
donnees['pm25'] = pd.to_numeric(donnees['pm25'], errors='coerce')
donnees['pm10'] = pd.to_numeric(donnees['pm10'], errors='coerce')

# Réglez les ordres ARIMA pour PM2.5 et PM10
p_pm25, d_pm25, q_pm25 = 1, 0, 3  # Ordres ARIMA pour PM2.5
p_pm10, d_pm10, q_pm10 = 1, 0, 3  # Ordres ARIMA pour PM10

# Créez un modèle ARIMA pour PM2.5 avec les ordres spécifiés
model_pm25 = sm.tsa.ARIMA(donnees['pm25'], order=(p_pm25, d_pm25, q_pm25))
# Créez un modèle ARIMA pour PM10 avec les ordres spécifiés
model_pm10 = sm.tsa.ARIMA(donnees['pm10'], order=(p_pm10, d_pm10, q_pm10))

# Ajustez les modèles aux données
model_fit_pm25 = model_pm25.fit()
model_fit_pm10 = model_pm10.fit()

# Obtenez la date actuelle avec l'heure au format "AAAA-MM-JJ HH:MM:SS"
date_actuelle = datetime.now()
date_actuelle_formattee = date_actuelle.strftime("%Y-%m-%d %H:%M:%S")

# Effectuez la prédiction pour le jour même (n) pour PM2.5 et PM10
forecast_n_pm25 = model_fit_pm25.get_forecast(steps=1)
forecasted_value_n_pm25 = round(forecast_n_pm25.predicted_mean.values[0], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm25 = int((forecasted_value_n_pm25 / 75) * 100)  # Calcul de l'IQA pour PM2.5

forecast_n_pm10 = model_fit_pm10.get_forecast(steps=1)
forecasted_value_n_pm10 = round(forecast_n_pm10.predicted_mean.values[0], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm10 = int((forecasted_value_n_pm10 / 150) * 100)  # Calcul de l'IQA pour PM10

# Générez le nom de la table en fonction de la date actuelle (n)
table_name_n = "prediction_" + date_actuelle.strftime("%Y%m%d")

# Créez un dataframe pour stocker les valeurs prédites pour 1 heure
predictions_1h_df = pd.DataFrame({
    'date': [date_actuelle_formattee],
    'PM2.5': [forecasted_value_n_pm25],
    'PM10': [forecasted_value_n_pm10],
    'IQA_PM2.5': [iqa_pm25],
    'IQA_PM10': [iqa_pm10]
})

# Utilisez SQLAlchemy pour créer la table si elle n'existe pas
with engine.connect() as conn, conn.begin():
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name_n} ("
                 "date DATETIME NOT NULL PRIMARY KEY,"
                 "PM25 FLOAT,"
                 "PM10 FLOAT,"
                 "IQA_PM25 INT,"
                 "IQA_PM10 INT"
                 ")")

# Utilisez SQLAlchemy pour insérer les données prédites pour 1 heure dans la table correspondante
with engine.connect() as conn, conn.begin():
    predictions_1h_df.to_sql(table_name_n, con=conn, if_exists='append', index=False)

print(f"Les valeurs prédites pour 1 heure ont été insérées dans la table '{table_name_n}'.")

# Effectuez la prédiction pour le jour suivant (n+1) pour PM2.5 et PM10
date_n1_pm25 = date_actuelle + timedelta(days=1)
forecast_n1_pm25 = model_fit_pm25.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+1 (24 heures)
forecasted_value_n1_pm25 = forecast_n1_pm25.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm25_n1 = (forecasted_value_n1_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

date_n1_pm10 = date_actuelle + timedelta(days=1)
forecast_n1_pm10 = model_fit_pm10.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+1 (24 heures)
forecasted_value_n1_pm10 = forecast_n1_pm10.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm10_n1 = (forecasted_value_n1_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Générez le nom de la table pour n+1
table_name_n1 = "prediction_" + date_n1_pm25.strftime("%Y%m%d")

# Créez un dataframe pour stocker les valeurs prédites pour n+1
predictions_n1_df = pd.DataFrame({
    'date': [date_n1_pm25.strftime("%Y-%m-%d %H:%M:%S")] * 24,
    'PM2.5': forecasted_value_n1_pm25,
    'PM10': forecasted_value_n1_pm10,
    'IQA_PM2.5': iqa_pm25_n1,
    'IQA_PM10': iqa_pm10_n1
})

# Utilisez SQLAlchemy pour créer la table si elle n'existe pas
with engine.connect() as conn, conn.begin():
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name_n1} ("
                 "date DATETIME NOT NULL PRIMARY KEY,"
                 "PM25 FLOAT,"
                 "PM10 FLOAT,"
                 "IQA_PM25 INT,"
                 "IQA_PM10 INT"
                 ")")

# Utilisez SQLAlchemy pour insérer les données prédites pour n+1 dans la table correspondante
with engine.connect() as conn, conn.begin():
    predictions_n1_df.to_sql(table_name_n1, con=conn, if_exists='append', index=False)

print(f"Les valeurs prédites pour n+1 ont été insérées dans la table '{table_name_n1}'.")

# Effectuez la prédiction pour le jour n+2 pour PM2.5 et PM10
date_n2_pm25 = date_n1_pm25 + timedelta(days=1)
forecast_n2_pm25 = model_fit_pm25.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+2 (24 heures)
forecasted_value_n2_pm25 = forecast_n2_pm25.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm25_n2 = (forecasted_value_n2_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

date_n2_pm10 = date_n1_pm10 + timedelta(days=1)
forecast_n2_pm10 = model_fit_pm10.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+2 (24 heures)
forecasted_value_n2_pm10 = forecast_n2_pm10.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm10_n2 = (forecasted_value_n2_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Générez le nom de la table pour n+2
table_name_n2 = "prediction_" + date_n2_pm25.strftime("%Y%m%d")

# Créez un dataframe pour stocker les valeurs prédites pour n+2
predictions_n2_df = pd.DataFrame({
    'date': [date_n2_pm25.strftime("%Y-%m-%d %H:%M:%S")] * 24,
    'PM2.5': forecasted_value_n2_pm25,
    'PM10': forecasted_value_n2_pm10,
    'IQA_PM2.5': iqa_pm25_n2,
    'IQA_PM10': iqa_pm10_n2
})

# Utilisez SQLAlchemy pour créer la table si elle n'existe pas
with engine.connect() as conn, conn.begin():
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name_n2} ("
                 "date DATETIME NOT NULL PRIMARY KEY,"
                 "PM25 FLOAT,"
                 "PM10 FLOAT,"
                 "IQA_PM25 INT,"
                 "IQA_PM10 INT"
                 ")")

# Utilisez SQLAlchemy pour insérer les données prédites pour n+2 dans la table correspondante
with engine.connect() as conn, conn.begin():
    predictions_n2_df.to_sql(table_name_n2, con=conn, if_exists='append', index=False)

print(f"Les valeurs prédites pour n+2 ont été insérées dans la table '{table_name_n2}'.")

# Effectuez la prédiction pour le jour n+3 pour PM2.5 et PM10
date_n3_pm25 = date_n2_pm25 + timedelta(days=1)
forecast_n3_pm25 = model_fit_pm25.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+3 (24 heures)
forecasted_value_n3_pm25 = forecast_n3_pm25.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm25_n3 = (forecasted_value_n3_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

date_n3_pm10 = date_n2_pm10 + timedelta(days=1)
forecast_n3_pm10 = model_fit_pm10.get_forecast(steps=24)  # Pour obtenir la prédiction pour n+3 (24 heures)
forecasted_value_n3_pm10 = forecast_n3_pm10.predicted_mean.values  # Récupérez les valeurs prédites
iqa_pm10_n3 = (forecasted_value_n3_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Générez le nom de la table pour n+3
table_name_n3 = "prediction_" + date_n3_pm25.strftime("%Y%m%d")

# Créez un dataframe pour stocker les valeurs prédites pour n+3
predictions_n3_df = pd.DataFrame({
    'date': [date_n3_pm25.strftime("%Y-%m-%d %H:%M:%S")] * 24,
    'PM2.5': forecasted_value_n3_pm25,
    'PM10': forecasted_value_n3_pm10,
    'IQA_PM2.5': iqa_pm25_n3,
    'IQA_PM10': iqa_pm10_n3
})

# Utilisez SQLAlchemy pour créer la table si elle n'existe pas
with engine.connect() as conn, conn.begin():
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name_n3} ("
                 "date DATETIME NOT NULL PRIMARY KEY,"
                 "PM25 FLOAT,"
                 "PM10 FLOAT,"
                 "IQA_PM25 INT,"
                 "IQA_PM10 INT"
                 ")")

# Utilisez SQLAlchemy pour insérer les données prédites pour n+3 dans la table correspondante
with engine.connect() as conn, conn.begin():
    predictions_n3_df.to_sql(table_name_n3, con=conn, if_exists='append', index=False)

print(f"Les valeurs prédites pour n+3 ont été insérées dans la table '{table_name_n3}'.")
