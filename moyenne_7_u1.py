import mysql.connector
from datetime import datetime, timedelta

# Fonction pour calculer la moyenne journalière
def calculate_daily_average(data):
    if data:
        return sum(data) / len(data)
    else:
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

# Date de début pour le calcul de la moyenne (24 septembre 2022)
start_date = datetime(2022, 12, 26)

# Date de fin (aujourd'hui)
end_date = datetime.now()

# Liste pour stocker les moyennes journalières
daily_averages = []

# Boucle pour calculer les moyennes journalières pour chaque jour
current_date = start_date
while current_date <= end_date:
    next_date = current_date + timedelta(days=1)

    # Sélection des données PM2.5, PM01, PM10, température et humidité pour la journée en cours, en excluant les valeurs manquantes et NaN
    cur.execute("""
        SELECT event, PM25, PM01, PM10, temperature, humidite
        FROM envir
        WHERE event >= %s AND event < %s
            AND PM25 IS NOT NULL AND PM25 != '' AND PM25 != 'NaN'
            AND PM01 IS NOT NULL AND PM01 != '' AND PM01 != 'NaN'
            AND PM10 IS NOT NULL AND PM10 != '' AND PM10 != 'NaN'
            AND temperature IS NOT NULL AND temperature != '' AND temperature != 'NaN'
            AND humidite IS NOT NULL AND humidite != '' AND humidite != 'NaN'
    """, (current_date, next_date))

    data = cur.fetchall()

    # Calcul de la moyenne journalière pour PM2.5
    pm25_m = calculate_daily_average([float(row[1]) for row in data])

    # Calcul de la moyenne journalière pour PM01
    pm01_m = calculate_daily_average([float(row[2]) for row in data])

    # Calcul de la moyenne journalière pour PM10
    pm10_m = calculate_daily_average([float(row[3]) for row in data])

    # Calcul de la moyenne journalière pour la température
    temperature_m = calculate_daily_average([float(row[4]) for row in data])

    # Calcul de la moyenne journalière pour l'humidité
    humidite_m = calculate_daily_average([float(row[5]) for row in data])

    # Ajouter les moyennes journalières à la liste
    daily_averages.append((current_date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m))

    # Passer à la journée suivante
    current_date = next_date

# Insertion des moyennes journalières dans une nouvelle table
for date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m in daily_averages:
    cur.execute("""
        INSERT INTO moyenne (event, pm25_m, pm01_m, pm10_m, temperature_m, humidity_m)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (date, pm25_m, pm01_m, pm10_m, temperature_m, humidite_m))
    print("Données insérées avec succès")

# Valider et fermer la connexion
conn.commit()
conn.close()
