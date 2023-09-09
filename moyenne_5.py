import mysql.connector
from datetime import datetime, timedelta
import math

# Fonction pour calculer la moyenne journalière en excluant les valeurs "nan"
def calculate_daily_average(data):
    valid_data = [value for value in data if not math.isnan(value)]
    if valid_data:
        return sum(valid_data) / len(valid_data)
    else:
        return 0.0

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pollution"
)

# Création d'un curseur
cur = conn.cursor()

# Date de début pour le calcul de la moyenne (24 septembre 2022)
start_date = datetime(2022, 9, 24)

# Date de fin (aujourd'hui)
end_date = datetime.now()

# Liste pour stocker les moyennes journalières
daily_averages = []

# Boucle pour calculer les moyennes journalières pour chaque jour
current_date = start_date
while current_date <= end_date:
    next_date = current_date + timedelta(days=1)

    # Sélection des données PM2.5, PM01, PM10, température et humidité pour la journée en cours, en excluant les valeurs "nan"
    cur.execute("""
        SELECT event, pm25, pm01, pm10, temperature, humidity
        FROM data
        WHERE event >= %s AND event < %s 
        AND pm25 IS NOT NULL AND pm25 != '' AND pm25 != 'nan'
        AND pm01 IS NOT NULL AND pm01 != '' AND pm01 != 'nan'
        AND pm10 IS NOT NULL AND pm10 != '' AND pm10 != 'nan'
        AND temperature IS NOT NULL AND temperature != '' AND temperature != 'nan'
        AND humidity IS NOT NULL AND humidity != '' AND humidity != 'nan'
    """, (current_date, next_date))

    data = cur.fetchall()

    # Calcul de la moyenne journalière pour chaque mesure
    pm25_m = calculate_daily_average([float(row[1]) for row in data])
    pm01_m = calculate_daily_average([float(row[2]) for row in data])
    pm10_m = calculate_daily_average([float(row[3]) for row in data])
    temperature_m = calculate_daily_average([float(row[4]) for row in data])
    humidity_m = calculate_daily_average([float(row[5]) for row in data])

    # Ajouter les moyennes journalières à la liste
    daily_averages.append((current_date, pm25_m, pm01_m, pm10_m, temperature_m, humidity_m))

    # Passer à la journée suivante
    current_date = next_date

# Insertion des moyennes journalières dans une nouvelle table
for date, pm25_avg, pm01_avg, pm10_avg, temp_avg, humidity_avg in daily_averages:
    cur.execute("""
        INSERT INTO moyenne (event, pm25_m, pm1_m, pm10_m, temperature_m, humidity_m)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (date, pm25_avg, pm01_avg, pm10_avg, temp_avg, humidity_avg))
    print("Données insérées avec succès")

# Valider et fermer la connexion
conn.commit()
conn.close()
