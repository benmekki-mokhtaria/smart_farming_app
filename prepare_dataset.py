import pandas as pd

# Chargement du dataset original
df = pd.read_csv("dataset_irrigation.csv")

# Remplissage des valeurs manquantes par la moyenne
num_cols = df.select_dtypes(include=['float64', 'int64']).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

# Sauvegarde
df.to_csv("dataset_irrigation_clean.csv", index=False)
print("Étape 1 terminée : dataset_irrigation_clean.csv créé.")