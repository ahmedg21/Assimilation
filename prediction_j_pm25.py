import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta
import schedule
import time

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = ''
hote = 'localhost'
base_de_donnees = 'poussiere'

# Fonction pour exécuter le script
def run():
    print("Exécution du script...")
    
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

    # Insérez la valeur prédite dans une nouvelle table
    cursor = connexion.cursor()
    insert_query = "INSERT INTO prediction (date, p_pm25) VALUES (%s, %s)"
    cursor.execute(insert_query, (date_demain, forecasted_value))
    connexion.commit()
    cursor.close()

    print("Prédiction pour demain (n+1):", forecasted_value)

# Planifiez l'exécution du script toutes les 24 heures
schedule.every(0.1).hours.do(run)

# Boucle pour exécuter le planificateur
while True:
    schedule.run_pending()
    time.sleep(1)
