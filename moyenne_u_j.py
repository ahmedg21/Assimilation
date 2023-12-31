import mysql.connector
from datetime import datetime, timedelta, date
import math

# Fonction pour calculer la moyenne journalière
def calculate_daily_average(data):
    if data:
        clean_data = [value for value in data if not math.isnan(value)]
        if clean_data:
            return sum(clean_data) / len(clean_data)
    return 0.0

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="poussiere"
)

# Création d'un curseur
cur = conn.cursor()

# Date de début (aujourd'hui) pour le calcul de la moyenne journalière
end_date = date.today()
start_date = end_date - timedelta(days=1)

# Sélection des données PM2.5, PM10, PM01, temperature et humidity pour la journée précédente, en excluant les valeurs manquantes et NaN
cur.execute("""
    SELECT event, PM25, PM10, PM01, temperature, humidite
    FROM envir
    WHERE event >= %s AND event < %s 
    AND (PM25 IS NOT NULL AND PM25 != '' AND PM25 NOT LIKE 'NaN%')
    AND (PM10 IS NOT NULL AND PM10 != '' AND PM10 NOT LIKE 'NaN%')
    AND (PM01 IS NOT NULL AND PM01 != '' AND PM01 NOT LIKE 'NaN%')
    AND (temperature IS NOT NULL AND temperature != '' AND temperature NOT LIKE 'NaN%')
    AND (humidite IS NOT NULL AND humidite != '' AND humidite NOT LIKE 'NaN%')
""", (start_date, end_date))

data = cur.fetchall()

# Extraction des données
pm25_data = [float(row[1]) for row in data]
pm10_data = [float(row[2]) for row in data]
pm01_data = [float(row[3]) for row in data]
temperature_data = [float(row[4]) for row in data]
humidity_data = [float(row[5]) for row in data]

# Calcul des moyennes journalières
pm25_m = calculate_daily_average(pm25_data)
pm10_m = calculate_daily_average(pm10_data)
pm01_m = calculate_daily_average(pm01_data)
temperature_m = calculate_daily_average(temperature_data)
humidity_m = calculate_daily_average(humidity_data)

# Insertion des moyennes journalières dans une nouvelle table
cur.execute("""
    INSERT INTO moyenne (event, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (start_date, pm25_m, pm10_m, pm01_m, temperature_m, humidity_m))

# Valider et fermer la connexion
conn.commit()
conn.close()
