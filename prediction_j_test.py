import pandas as pd
import numpy as np
import mysql.connector
import statsmodels.api as sm
from datetime import datetime, timedelta
import schedule
import time
from sqlalchemy import create_engine

# Spécifiez les informations de connexion à votre base de données MySQL
# Remplacez 'votre_nom_utilisateur', 'votre_mot_de_passe', 'votre_hôte', 'votre_base_de_données'
nom_utilisateur = 'root'
mot_de_passe = ''
hote = 'localhost'
base_de_donnees = 'poussiere'

# Fonction pour exécuter le script
def run():
    print("Exécution du script...")
    
    # Établissez une connexion à la base de données MySQL en utilisant SQLAlchemy
    db_uri = f"mysql://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}"
    engine = create_engine(db_uri)
    
    # Chargez vos données depuis la base de données en utilisant SQLAlchemy connection
    requete_sql = 'SELECT event, PM25 FROM envir WHERE event >= CURDATE() - INTERVAL 30 DAY'
    donnees = pd.read_sql_query(requete_sql, engine)

    # Réglez les ordres ARIMA
    p, d, q = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés

    # Assurez-vous que 'pm25_m' est une série 1D
    pm25_series = donnees['PM25'].squeeze()

    # Créez un modèle ARIMA avec les ordres spécifiés
    model = sm.tsa.ARIMA(pm25_series, order=(p, d, q))

    # Ajustez le modèle aux données
    model_fit = model.fit()

    # Effectuez la prédiction pour le jour suivant (n+1)
    date_demain = datetime.now() + timedelta(days=1)
    forecast = model_fit.get_forecast(steps=1)

    # Récupérez la valeur prédite pour demain
    forecasted_value = forecast.predicted_mean.values[0]

    # Insérez la valeur prédite dans une nouvelle table
    connexion = mysql.connector.connect(
        user=nom_utilisateur,
        password=mot_de_passe,
        host=hote,
        database=base_de_donnees
    )
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
