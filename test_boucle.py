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
requete_sql = 'SELECT event, pm25_m FROM data_j WHERE event >= CURDATE() - INTERVAL 30 DAY'
donnees = pd.read_sql_query(requete_sql, engine)

# Réglez les ordres ARIMA
p, d, q = 1, 0, 3  # Remplacez par les ordres ARIMA appropriés

# Créez un modèle ARIMA avec les ordres spécifiés
model = sm.tsa.ARIMA(donnees['pm25_m'], order=(p, d, q))

# Ajustez le modèle aux données
model_fit = model.fit()

# Obtenez l'heure actuelle
heure_actuelle = datetime.now()

# Définissez le nombre de jours pour lesquels vous souhaitez faire des prédictions
nombre_jours = 3  # Par exemple, pour les trois prochains jours

# Boucle pour effectuer des prédictions pour les jours à venir
for i in range(nombre_jours):
    # Calculez la date pour la prédiction
    date_prediction = heure_actuelle + timedelta(days=i)
    
    # Effectuez la prédiction pour la date calculée
    forecast = model_fit.get_forecast(steps=1)
    forecasted_value = forecast.predicted_mean.values[0]
    
    # Affichez la date de la prédiction et la valeur prédite correspondante
    print(f"Prédiction pour le jour {i+1} - Date: {date_prediction}, Valeur: {forecasted_value}")
