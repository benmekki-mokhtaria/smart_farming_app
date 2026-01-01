import pandas as pd # Chargement de la bibliothèque pour la manipulation des données
from sklearn.ensemble import RandomForestRegressor # Import de l'algorithme de régression par Forêts Aléatoires
from sklearn.preprocessing import LabelEncoder # Import de l'outil pour transformer le texte en données numériques
import pickle # Bibliothèque pour la sérialisation et sauvegarde du modèle
import os # Module pour la gestion des dossiers et fichiers système

def train(): # Définition de la fonction d'entraînement du modèle
    if not os.path.exists('models'): os.makedirs('models') # Création du dossier 'models' s'il n'existe pas
    df = pd.read_csv('dataset_irrigation_clean.csv') # Lecture du jeu de données nettoyé
    
    # Encodage des colonnes texte
    encoders = {} # Initialisation d'un dictionnaire pour stocker les transformateurs de texte
    for col in ['soil_type', 'water_source_type', 'label']: # Boucle sur les variables catégorielles
        le = LabelEncoder() # Instanciation de l'encodeur
        df[col] = le.fit_transform(df[col].astype(str)) # Conversion des textes en nombres
        encoders[col] = le # Sauvegarde de l'encodeur pour une utilisation future
        
    X = df.drop('water_usage_efficiency', axis=1) # Définition des variables explicatives (features)
    y = df['water_usage_efficiency'] # Définition de la variable cible (efficience de l'eau)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42) # Configuration du modèle (100 arbres)
    model.fit(X, y) # Entraînement du modèle sur les données
    
    # On sauvegarde TOUT dans un seul fichier pour simplifier
    with open('models/model.pkl', 'wb') as f: # Ouverture du fichier de destination en mode binaire
        pickle.dump({'model': model, 'encoders': encoders, 'columns': list(X.columns)}, f) # Archivage du modèle et des paramètres
    print("Étape 2 terminée : models/model.pkl créé.") # Message de confirmation de fin d'exécution

if __name__ == "__main__": # Point d'entrée principal du script
    train() # Appel de la fonction de formation