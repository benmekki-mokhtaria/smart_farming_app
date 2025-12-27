import sqlite3
import os

# Supprime l'ancienne base pour éviter les conflits
if os.path.exists("database.db"):
    os.remove("database.db")

conn = sqlite3.connect("database.db")
# Création de la table avec TOUTES les colonnes pour le tableau
conn.execute('''CREATE TABLE predictions 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              n_val REAL, 
              p_val REAL, 
              k_val REAL, 
              temperature REAL, 
              result REAL)''')

# Ajout de l'utilisateur admin
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")

conn.commit()
conn.close()
print("Base de données réinitialisée avec succès !")