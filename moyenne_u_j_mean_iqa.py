import mysql.connector
from datetime import datetime, timedelta
import statistics

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

# Date de fin (hier)
end_date = datetime.now() - timedelta(days=1)

# Liste pour stocker les moyennes journalières
daily_averages = []

# Boucle pour calculer les moyennes journalières pour chaque jour
current_date = start_date
while current_date <= end_date:
    next_date = current_date + timedelta(days=1)

    # Sélection des données PM2.5, PM01, PM10, température et humidité pour la journée en cours, en excluant les valeurs manquantes et NaN
    cur.execute("""
        SELECT event, pm25, pm01, pm10, temperature, humidity
        FROM data
        WHERE event >= %s AND event < %s
            AND pm25 IS NOT NULL AND pm25 != '' AND pm25 != 'NaN'
            AND pm01 IS NOT NULL AND pm01 != '' AND pm01 != 'NaN'
            AND pm10 IS NOT NULL AND pm10 != '' AND pm10 != 'NaN'
            AND temperature IS NOT NULL AND temperature != '' AND temperature != 'NaN'
            AND humidity IS NOT NULL AND humidity != '' AND humidity != 'NaN'
    """, (current_date, next_date))

    data = cur.fetchall()

    # Vérifier si la liste de données n'est pas vide
    if data:
        # Calcul de la moyenne journalière pour PM2.5
        pm25_m = statistics.mean([float(row[1]) for row in data])

        # Calcul de la moyenne journalière pour PM01
        pm01_m = statistics.mean([float(row[2]) for row in data])

        # Calcul de la moyenne journalière pour PM10
        pm10_m = statistics.mean([float(row[3]) for row in data])

        # Calcul de la moyenne journalière pour la température
        temperature_m = statistics.mean([float(row[4]) for row in data])

        # Calcul de la moyenne journalière pour l'humidité
        humidite_m = statistics.mean([float(row[5]) for row in data])

        # Calcul de l'IQA pour PM2.5
        iqa_pm25 = (pm25_m / 75) * 100

        # Calcul de l'IQA pour PM10
        iqa_pm10 = (pm10_m / 150) * 100

        # Ajouter les moyennes journalières à la liste
        daily_averages.append((current_date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m, iqa_pm25, iqa_pm10))

    # Passer à la journée suivante
    current_date = next_date

# Insertion des moyennes journalières dans une nouvelle table
for date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m, iqa_pm25, iqa_pm10 in daily_averages:
    cur.execute("""
        INSERT INTO moyenne (event, pm25_m, pm01_m, pm10_m, temperature_m, humidity_m, iqa_pm25, iqa_pm10)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m, iqa_pm25, iqa_pm10))
    print("Données insérées avec succès")

# Valider et fermer la connexion
conn.commit()
conn.close()
