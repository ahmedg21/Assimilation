import mysql.connector
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import pandas as pd
import statsmodels.api as sm

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = '150421Ah'
hote = 'localhost'
base_de_donnees = 'pollution'

def effectuer_prediction(connexion, donnees, p, d, q, colonne):
    model = sm.tsa.ARIMA(donnees[colonne], order=(p, d, q))
    model_fit = model.fit()
    forecast = model_fit.get_forecast(steps=1)
    forecasted_value = forecast.predicted_mean.values[0]
    forecasted_value_int = int(forecasted_value)
    return forecasted_value_int

try:
    # Établissez une connexion à la base de données MySQL en utilisant SQLAlchemy
    connexion_string = f'mysql+mysqlconnector://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}'
    engine = create_engine(connexion_string)

    # Chargez vos données depuis la base de données en utilisant Pandas
    # Remplacez 'votre_requete_sql_pm25' par votre propre requête SQL pour récupérer les données PM2.5
    requete_sql_pm25 = 'SELECT event, pm25_m FROM data WHERE event >= CURDATE() - INTERVAL 30 DAY'
    donnees_pm25 = pd.read_sql_query(requete_sql_pm25, engine)

    # Chargez vos données PM10 depuis la base de données en utilisant Pandas
    # Remplacez 'votre_requete_sql_pm10' par votre propre requête SQL pour récupérer les données PM10
    requete_sql_pm10 = 'SELECT event, pm10_m FROM data WHERE event >= CURDATE() - INTERVAL 30 DAY'
    donnees_pm10 = pd.read_sql_query(requete_sql_pm10, engine)

    # Réglez les ordres ARIMA pour le PM2.5 et le PM10
    p_pm25, d_pm25, q_pm25 = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés pour le PM2.5
    p_pm10, d_pm10, q_pm10 = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés pour le PM10

    # Effectuer la prédiction PM2.5
    forecasted_value_pm25_int = effectuer_prediction(engine, donnees_pm25, p_pm25, d_pm25, q_pm25, 'pm25_m')

    # Effectuer la prédiction PM10
    forecasted_value_pm10_int = effectuer_prediction(engine, donnees_pm10, p_pm10, d_pm10, q_pm10, 'pm10_m')

    # Insérez les valeurs prédites (entières) et la date dans la table "prediction_p"
    date_demain = datetime.now() + timedelta(days=1)
    connexion = mysql.connector.connect(
        user=nom_utilisateur,
        password=mot_de_passe,
        host=hote,
        database=base_de_donnees
    )
    cursor = connexion.cursor()
    insert_query = "INSERT INTO prediction_p (date, pm25_p, pm10_p) VALUES (%s, %s, %s)"
    data_to_insert = (date_demain, forecasted_value_pm25_int, forecasted_value_pm10_int)
    cursor.execute(insert_query, data_to_insert)
    connexion.commit()
    cursor.close()

    print("Prédiction pour demain (n+1) PM2.5:", forecasted_value_pm25_int)
    print("Prédiction pour demain (n+1) PM10:", forecasted_value_pm10_int)

except Exception as e:
    print("Une erreur s'est produite :", str(e))
    # Ajoutez ici la gestion des erreurs, par exemple, enregistrer les erreurs dans un fichier journal.
finally:
    if 'connexion' in locals() and connexion.is_connected():
        connexion.close()
