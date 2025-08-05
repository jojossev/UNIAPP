import sqlite3
import os

# Chemin vers la base de données SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'db.sqlite3')

# Se connecter à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vérifier si la table reviews_review existe
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='reviews_review';
""")

# Récupérer les résultats
table_exists = cursor.fetchone()

if table_exists:
    print("La table 'reviews_review' existe dans la base de données.")
    
    # Afficher la structure de la table
    cursor.execute("PRAGMA table_info(reviews_review)")
    columns = cursor.fetchall()
    print("\nStructure de la table 'reviews_review':")
    for column in columns:
        print(f"- {column[1]} ({column[2]})")
else:
    print("La table 'reviews_review' n'existe PAS dans la base de données.")
    
    # Afficher toutes les tables existantes
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name;
    """)
    tables = cursor.fetchall()
    print("\nTables existantes dans la base de données:")
    for table in tables:
        print(f"- {table[0]}")

# Fermer la connexion
conn.close()
