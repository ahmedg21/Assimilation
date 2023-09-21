import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta, date
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
requete_sql = "SELECT event, pm25_m, pm10_m FROM data WHERE event <= CURDATE()"
donnees = pd.read_sql_query(requete_sql, engine)
donnees['pm25'] = pd.to_numeric(donnees['pm25'], errors='coerce')
donnees['pm10'] = pd.to_numeric(donnees['pm10'], errors='coerce')

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

# Obtenez la date actuelle (sans heure)
date_actuelle = datetime.now()

# Effectuez la prédiction pour le jour même (n) pour PM2.5
forecast_n_pm25 = model_fit_pm25.get_forecast(steps=1)
forecasted_value_n_pm25 = round(forecast_n_pm25.predicted_mean.values[0], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm25 = (forecasted_value_n_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

# Effectuez la prédiction pour le jour même (n) pour PM10
forecast_n_pm10 = model_fit_pm10.get_forecast(steps=1)
forecasted_value_n_pm10 = round(forecast_n_pm10.predicted_mean.values[0], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm10 = (forecasted_value_n_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Effectuez la prédiction pour le jour suivant (n+1) pour PM2.5
date_demain = date_actuelle + timedelta(days=1)
forecast_n1_pm25 = model_fit_pm25.get_forecast(steps=2)
forecasted_value_n1_pm25 = round(forecast_n1_pm25.predicted_mean.values[1], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm25_n1 = (forecasted_value_n1_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

# Effectuez la prédiction pour le jour suivant (n+1) pour PM10
forecast_n1_pm10 = model_fit_pm10.get_forecast(steps=2)
forecasted_value_n1_pm10 = round(forecast_n1_pm10.predicted_mean.values[1], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm10_n1 = (forecasted_value_n1_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Effectuez la prédiction pour le jour après-demain (n+2) pour PM2.5
date_apres_demain = date_demain + timedelta(days=1)
forecast_n2_pm25 = model_fit_pm25.get_forecast(steps=3)
forecasted_value_n2_pm25 = round(forecast_n2_pm25.predicted_mean.values[2], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm25_n2 = (forecasted_value_n2_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

# Effectuez la prédiction pour le jour après-demain (n+2) pour PM10
forecast_n2_pm10 = model_fit_pm10.get_forecast(steps=3)
forecasted_value_n2_pm10 = round(forecast_n2_pm10.predicted_mean.values[2], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm10_n2 = (forecasted_value_n2_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Effectuez la prédiction pour le jour n+3 pour PM2.5
date_n3_pm25 = date_apres_demain + timedelta(days=1)
forecast_n3_pm25 = model_fit_pm25.get_forecast(steps=4)
forecasted_value_n3_pm25 = round(forecast_n3_pm25.predicted_mean.values[3], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm25_n3 = (forecasted_value_n3_pm25 / 75) * 100  # Calcul de l'IQA pour PM2.5

# Effectuez la prédiction pour le jour n+3 pour PM10
forecast_n3_pm10 = model_fit_pm10.get_forecast(steps=4)
forecasted_value_n3_pm10 = round(forecast_n3_pm10.predicted_mean.values[3], 2)  # Arrondir à 2 chiffres après la virgule
iqa_pm10_n3 = (forecasted_value_n3_pm10 / 150) * 100  # Calcul de l'IQA pour PM10

# Créez un dataframe pour stocker les valeurs prédites et l'IQA
predictions_df = pd.DataFrame({
    'date': [date_actuelle, date_demain, date_apres_demain, date_n3_pm25],
    'PM2.5': [forecasted_value_n_pm25, forecasted_value_n1_pm25, forecasted_value_n2_pm25, forecasted_value_n3_pm25],
    'PM10': [forecasted_value_n_pm10, forecasted_value_n1_pm10, forecasted_value_n2_pm10, forecasted_value_n3_pm10],
    'IQA_PM2.5': [iqa_pm25, iqa_pm25_n1, iqa_pm25_n2, iqa_pm25_n3],
    'IQA_PM10': [iqa_pm10, iqa_pm10_n1, iqa_pm10_n2, iqa_pm10_n3]
})

# Utilisez SQLAlchemy pour insérer ou mettre à jour les données prédites dans la table "prediction"
with engine.connect() as conn, conn.begin():
    for index, row in predictions_df.iterrows():
        # Vérifier si la date existe déjà dans la table "prediction"
        query = text(f"SELECT COUNT(*) FROM prediction_u WHERE DATE(date) = :date")
        result = conn.execute(query, {'date': row['date']}).fetchone()

        if result[0] == 0:
            # Si la date n'existe pas, insérer une nouvelle ligne
            insert_query = text(f"INSERT INTO prediction_u (date, PM25, PM10, IQA_PM25, IQA_PM10) VALUES (:date, :pm25, :pm10, :iqa_pm25, :iqa_pm10)")
            conn.execute(insert_query, {'date': row['date'], 'pm25': row['PM2.5'], 'pm10': row['PM10'], 'iqa_pm25': row['IQA_PM2.5'], 'iqa_pm10': row['IQA_PM10']})
            print('bou bess')
        else:
            # Si la date existe, mettre à jour les valeurs
            update_query = text(f"UPDATE prediction_u SET PM25 = :pm25, PM10 = :pm10, IQA_PM25 = :iqa_pm25, IQA_PM10 = :iqa_pm10 WHERE DATE(date) = :date")
            conn.execute(update_query, {'date': row['date'], 'pm25': row['PM2.5'], 'pm10': row['PM10'], 'iqa_pm25': row['IQA_PM2.5'], 'iqa_pm10': row['IQA_PM10']})
            print('yessal nagnouko')

print("Les valeurs prédites et l'IQA ont été insérées ou mises à jour dans la table 'prediction'.")
