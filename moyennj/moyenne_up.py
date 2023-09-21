from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, date
import math
import statistics

# Informations de connexion MySQL
nom_utilisateur = 'root'
mot_de_passe = '150421Ah'
hote = 'localhost'
base_de_donnees = 'pollution'

# Créez une connexion à la base de données MySQL en utilisant SQLAlchemy
connexion_uri = f"mysql+mysqlconnector://{nom_utilisateur}:{mot_de_passe}@{hote}/{base_de_donnees}"
engine = create_engine(connexion_uri)

# Date de début (aujourd'hui) pour le calcul de la moyenne journalière
end_date = date.today()
start_date = end_date - timedelta(days=1)

# Sélection des données PM2.5, PM10, PM01, temperature et humidity pour la journée précédente, en excluant les valeurs manquantes et NaN
with engine.connect() as conn, conn.begin():
    query = text("""
        SELECT event, pm25, pm01, pm10, temperature, humidity
        FROM data
        WHERE event >= :start_date AND event < :end_date
            AND pm25 IS NOT NULL AND pm25 != '' AND pm25 != 'NaN'
            AND pm01 IS NOT NULL AND pm01 != '' AND pm01 != 'NaN'
            AND pm10 IS NOT NULL AND pm10 != '' AND pm10 != 'NaN'
            AND temperature IS NOT NULL AND temperature != '' AND temperature != 'NaN'
            AND humidity IS NOT NULL AND humidity != '' AND humidity != 'NaN'
    """), {'start_date': start_date, 'end_date': end_date})

    data = cur.fetchall()

# Extraction des données
pm25_data = [float(row[1]) for row in data]
pm01_data = [float(row[2]) for row in data]
pm10_data = [float(row[3]) for row in data]
temperature_data = [float(row[4]) for row in data]
humidity_data = [float(row[5]) for row in data]

# Calcul des moyennes journalières avec statistics.mean
pm25_m = statistics.mean(pm25_data)
pm01_m = statistics.mean(pm01_data)
pm10_m = statistics.mean(pm10_data)
temperature_m = statistics.mean(temperature_data)
humidity_m = statistics.mean(humidity_data)

# Calcul de l'IQA pour PM2.5 et PM10
iqa_pm25 = (pm25_m / 75) * 100
iqa_pm10 = (pm10_m / 150) * 100

# Créer une session SQLAlchemy pour gérer les opérations d'insertion/mise à jour
with engine.connect() as conn, conn.begin():
    # Vérifier si la date existe déjà dans la table "data_j"
    query = text("SELECT COUNT(*) FROM data_j WHERE DATE(event) = :date")
    result = conn.execute(query, {'date': start_date}).fetchone()

    if result[0] == 0:
        # Si la date n'existe pas, insérer une nouvelle ligne
        insert_query = text("INSERT INTO data_j (event, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m, iqa_pm25, iqa_pm10) VALUES (:date, :pm25, :pm10, :pm01, :temperature, :humidity, :iqa_pm25, :iqa_pm10)")
        conn.execute(insert_query, {'date': start_date, 'pm25': pm25_m, 'pm10': pm10_m, 'pm01': pm01_m, 'temperature': temperature_m, 'humidity': humidity_m, 'iqa_pm25': iqa_pm25, 'iqa_pm10': iqa_pm10})
        print('Nouvelle ligne insérée.')
    else:
        # Si la date existe, mettre à jour les valeurs
        update_query = text("UPDATE data_j SET pm25_m = :pm25, pm10_m = :pm10, pm01_m = :pm01, temperature_m = :temperature, humidity_m = :humidity, iqa_pm25 = :iqa_pm25, iqa_pm10 = :iqa_pm10 WHERE DATE(event) = :date")
        conn.execute(update_query, {'date': start_date, 'pm25': pm25_m, 'pm10': pm10_m, 'pm01': pm01_m, 'temperature': temperature_m, 'humidity': humidity_m, 'iqa_pm25': iqa_pm25, 'iqa_pm10': iqa_pm10})
        print('Ligne mise à jour.')
