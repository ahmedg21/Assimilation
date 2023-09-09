import mysql.connector
from datetime import datetime, timedelta

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="pollution"
)

# Création d'un curseur
cur = conn.cursor()

# Date de début et de fin pour le calcul de la moyenne journalière
start_date = datetime(2022, 10, 17)
end_date = datetime(2022, 10, 18)

# Sélection des données PM2.5 pour la journée spécifiée, en excluant les valeurs manquantes
cur.execute("""
    SELECT event, pm25
    FROM data
    WHERE event >= %s AND event < %s AND pm25 IS NOT NULL AND pm25 != ''
""", (start_date, end_date))

data = cur.fetchall()

# Vérifier si des données existent pour la période spécifiée
if data:
    # Convertir les valeurs de la colonne pm25 en nombres flottants
    data = [(row[0], float(row[1])) for row in data]

    # Calcul de la moyenne journalière
    pm25_m = sum(row[1] for row in data) / len(data)

    # Insertion de la moyenne journalière dans une nouvelle table
    cur.execute("""
        INSERT INTO moyenne (event, pm25_m)
        VALUES (%s, %s)
    """, (start_date, pm25_m))
    print("Donnée insérée")
else:
    print("Aucune donnée trouvée pour la période spécifiée.")

# Valider et fermer la connexion
conn.commit()
conn.close()
