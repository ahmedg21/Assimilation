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

# Définissez le nombre d'heures à prédire
nombre_heures_a_predire = 2  # Par exemple, pour prédire les 24 prochaines heures

# Créez une liste pour stocker les prédictions horaires
predictions_horaires = []

# Itérez sur le nombre d'heures à prédire
for _ in range(nombre_heures_a_predire):
    # Effectuez la prédiction pour PM2.5 pour cette heure
    forecast_pm25 = model_fit_pm25.get_forecast(steps=1)
    forecasted_value_pm25 = round(forecast_pm25.predicted_mean.values[0], 2)
    iqa_pm25 = int((forecasted_value_pm25 / 75) * 100)

    # Effectuez la prédiction pour PM10 pour cette heure
    forecast_pm10 = model_fit_pm10.get_forecast(steps=1)
    forecasted_value_pm10 = round(forecast_pm10.predicted_mean.values[0], 2)
    iqa_pm10 = int((forecasted_value_pm10 / 150) * 100)

    # Ajoutez les prédictions à la liste
    predictions_horaires.append({
        'date': date_actuelle.strftime("%Y-%m-%d %H:%M:%S"),
        'PM2.5': forecasted_value_pm25,
        'PM10': forecasted_value_pm10,
        'IQA_PM2.5': iqa_pm25,
        'IQA_PM10': iqa_pm10
    })

    # Avancez d'une heure pour la prochaine prédiction
    date_actuelle += timedelta(hours=1)

# Créez un dataframe pour stocker les valeurs prédites et l'IQA dans la table "prediction_h"
predictions_df_h = pd.DataFrame(predictions_horaires)

# Utilisez SQLAlchemy pour insérer ou mettre à jour les données prédites dans la table "prediction_h"
with engine.connect() as conn, conn.begin():
    for index, row in predictions_df_h.iterrows():
        # Vérifier si la date existe déjà dans la table "prediction_h"
        query = text(f"SELECT COUNT(*) FROM prediction_1h WHERE DATE(date) = :date")
        result = conn.execute(query, {'date': row['date']}).fetchone()

        if result[0] == 0:
            # Si la date n'existe pas, insérer une nouvelle ligne dans la table "prediction_h"
            insert_query = text(f"INSERT INTO prediction_1h (date, PM25, PM10, IQA_PM25, IQA_PM10) VALUES (:date, :pm25, :pm10, :iqa_pm25, :iqa_pm10)")
            conn.execute(insert_query, {'date': row['date'], 'pm25': row['PM2.5'], 'pm10': row['PM10'], 'iqa_pm25': row['IQA_PM2.5'], 'iqa_pm10': row['IQA_PM10']})
            print('bou bess')
        else:
            # Si la date existe, mettre à jour les valeurs dans la table "prediction_h"
            update_query = text(f"UPDATE prediction_1h SET PM25 = :pm25, PM10 = :pm10, IQA_PM25 = :iqa_pm25, IQA_PM10 = :iqa_pm10 WHERE DATE(date) = :date")
            conn.execute(update_query, {'date': row['date'], 'pm25': row['PM2.5'], 'pm10': row['PM10'], 'iqa_pm25': row['IQA_PM2.5'], 'iqa_pm10': row['IQA_PM10']})
            print('yessal nagnouko')

print("Les valeurs prédites et l'IQA ont été insérées ou mises à jour dans la table 'prediction_h'.")
