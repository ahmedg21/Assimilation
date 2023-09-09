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

    # Sélection des données PM2.5 pour la journée en cours, en excluant les valeurs manquantes
    cur.execute("""
        SELECT event, PM25
        FROM envir
        WHERE event >= %s AND event < %s AND PM25 IS NOT NULL AND PM25 != ''
    """, (current_date, next_date))

    data = cur.fetchall()

    # Calcul de la moyenne journalière
    pm25_m = calculate_daily_average([float(row[1]) for row in data])

    # Ajouter la moyenne journalière à la liste
    daily_averages.append((current_date, pm25_m))

    # Passer à la journée suivante
    current_date = next_date

# Insertion des moyennes journalières dans une nouvelle table
for date, average in daily_averages:
    cur.execute("""
        INSERT INTO moyenne (event, pm25_m)
        VALUES (%s, %s)
    """, (date, average))
    print("Donnée insérée avec succes")

# Valider et fermer la connexion
conn.commit()
conn.close()
