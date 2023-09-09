import mysql.connector
from datetime import datetime, timedelta, date

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
    database="pollution"
)

# Création d'un curseur
cur = conn.cursor()

# Date de début (aujourd'hui) pour le calcul de la moyenne journalière
end_date = date.today()
start_date = end_date - timedelta(days=1)

# Sélection des données PM2.5 pour la journée précédente, en excluant les valeurs manquantes
cur.execute("""
    SELECT event, pm25
    FROM data
    WHERE event >= %s AND event < %s AND pm25 IS NOT NULL AND pm25 != ''
""", (start_date, end_date))

data = cur.fetchall()

# Calcul de la moyenne journalière
pm25_m = calculate_daily_average([float(row[1]) for row in data])

# Insertion de la moyenne journalière dans une nouvelle table
cur.execute("""
    INSERT INTO moyenne (event, pm25_m)
    VALUES (%s, %s)
""", (start_date, pm25_m))

# Valider et fermer la connexion
conn.commit()
conn.close()
