import mysql.connector
from datetime import datetime, timedelta, date
import math
import statistics  # Import de la bibliothèque statistics

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pollution"
)

# Création d'un curseur
cur = conn.cursor()

# Date de début (aujourd'hui) pour le calcul de la moyenne journalière
end_date = date.today()
start_date = end_date - timedelta(days=1)

# Sélection des données PM2.5, PM10, PM01, temperature et humidity pour la journée précédente, en excluant les valeurs manquantes et NaN
cur.execute("""
    SELECT event, pm25, pm10, pm01, temperature, humidity
    FROM data
    WHERE event >= %s AND event < %s 
    AND (pm25 IS NOT NULL AND pm25 != '' AND pm25 NOT LIKE 'NaN%')
    AND (pm10 IS NOT NULL AND pm10 != '' AND pm10 NOT LIKE 'NaN%')
    AND (pm01 IS NOT NULL AND pm01 != '' AND pm01 NOT LIKE 'NaN%')
    AND (temperature IS NOT NULL AND temperature != '' AND temperature NOT LIKE 'NaN%')
    AND (humidity IS NOT NULL AND humidity != '' AND humidity NOT LIKE 'NaN%')
""", (start_date, end_date))

data = cur.fetchall()

# Extraction des données
pm25_data = [float(row[1]) for row in data]
pm10_data = [float(row[2]) for row in data]
pm01_data = [float(row[3]) for row in data]
temperature_data = [float(row[4]) for row in data]
humidity_data = [float(row[5]) for row in data]

# Calcul des moyennes journalières avec statistics.mean
pm25_m = statistics.mean(pm25_data)
pm10_m = statistics.mean(pm10_data)
pm01_m = statistics.mean(pm01_data)
temperature_m = statistics.mean(temperature_data)
humidity_m = statistics.mean(humidity_data)

# Insertion des moyennes journalières dans une nouvelle table
cur.execute("""
    INSERT INTO moyenne (event, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (start_date, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m))

# Valider et fermer la connexion
conn.commit()
conn.close()
