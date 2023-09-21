from datetime import datetime, timedelta, date
import math
import statistics
from sqlalchemy import create_engine, text

# Informations de connexion MySQL
nom_utilisateur = 'root'
mot_de_passe = '150421Ah'
hote = 'localhost'
base_de_donnees = 'pollution'

# Créez une connexion à la base de données MySQL en utilisant SQLAlchemy
connexion_uri = f"mysql+mysqlconnector://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}"
engine = create_engine(connexion_uri)

# Date et heure actuelles
now = datetime.now()
date_now = now.date()  # Extraction de la date seulement

# Sélection des données PM2.5, PM10, PM01, temperature et humidity depuis minuit jusqu'à maintenant
with engine.connect() as conn, conn.begin():
    query = text("""
        SELECT event, pm25, pm10, pm01, temperature, humidity
        FROM data
        WHERE event >= :start_time AND event <= :end_time
        AND (pm25 IS NOT NULL AND pm25 != '' AND pm25 NOT LIKE 'NaN%')
        AND (pm10 IS NOT NULL AND pm10 != '' AND pm10 NOT LIKE 'NaN%')
        AND (pm01 IS NOT NULL AND pm01 != '' AND pm01 NOT LIKE 'NaN%')
        AND (temperature IS NOT NULL AND temperature != '' AND temperature NOT LIKE 'NaN%')
        AND (humidity IS NOT NULL AND humidity != '' AND humidity NOT LIKE 'NaN%')
    """)
    data = conn.execute(query, {'start_time': date_now, 'end_time': now}).fetchall()

# Extraction des données
pm25_data = [float(row[1]) for row in data]
pm10_data = [float(row[2]) for row in data]
pm01_data = [float(row[3]) for row in data]
temperature_data = [float(row[4]) for row in data]
humidity_data = [float(row[5]) for row in data]

# Calcul des moyennes pour les données dans la plage horaire spécifiée avec statistics.mean
pm25_m = statistics.mean(pm25_data)
pm10_m = statistics.mean(pm10_data)
pm01_m = statistics.mean(pm01_data)
temperature_m = statistics.mean(temperature_data)
humidity_m = statistics.mean(humidity_data)

# Calcul de l'IQA pour pm25 et pm10
iqa_pm25 = (pm25_m / 75) * 100
iqa_pm10 = (pm10_m / 150) * 100

# Utilisez SQLAlchemy pour insérer ou mettre à jour les données dans la table "data_j"
with engine.connect() as conn, conn.begin():
    # Vérifier si la date existe déjà dans la table "data_j"
    query = text("SELECT COUNT(*) FROM data_j WHERE DATE(event) = :date")
    result = conn.execute(query, {'date': date_now}).fetchone()

    if result[0] == 0:
        # Si la date n'existe pas, insérer une nouvelle ligne
        insert_query = text("INSERT INTO data_j (event, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m, iqa_pm25, iqa_pm10) VALUES (:date, :pm25, :pm10, :pm01, :temperature, :humidity, :iqa_pm25, :iqa_pm10)")
        conn.execute(insert_query, {'date': date_now, 'pm25': pm25_m, 'pm10': pm10_m, 'pm01': pm01_m, 'temperature': temperature_m, 'humidity': humidity_m, 'iqa_pm25': iqa_pm25, 'iqa_pm10': iqa_pm10})
        print('Nouvelle ligne insérée.')
    else:
        # Si la date existe, mettre à jour les valeurs
        update_query = text("UPDATE data_j SET pm25_m = :pm25, pm10_m = :pm10, pm01_m = :pm01, temperature_m = :temperature, humidity_m = :humidity, iqa_pm25 = :iqa_pm25, iqa_pm10 = :iqa_pm10 WHERE DATE(event) = :date")
        conn.execute(update_query, {'date': date_now, 'pm25': pm25_m, 'pm10': pm10_m, 'pm01': pm01_m, 'temperature': temperature_m, 'humidity': humidity_m, 'iqa_pm25': iqa_pm25, 'iqa_pm10': iqa_pm10})
        print('Ligne mise à jour.')

# Valider et fermer la connexion
conn.commit()
conn.close()
