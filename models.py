import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

def train():
    if not os.path.exists('models'): os.makedirs('models')
    df = pd.read_csv('dataset_irrigation_clean.csv')
    
    # Encodage des colonnes texte
    encoders = {}
    for col in ['soil_type', 'water_source_type', 'label']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
        
    X = df.drop('water_usage_efficiency', axis=1)
    y = df['water_usage_efficiency']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # On sauvegarde TOUT dans un seul fichier pour simplifier
    with open('models/model.pkl', 'wb') as f:
        pickle.dump({'model': model, 'encoders': encoders, 'columns': list(X.columns)}, f)
    print("Étape 2 terminée : models/model.pkl créé.")

if __name__ == "__main__":
    train()