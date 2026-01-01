import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder # Pour transformer le texte en chiffres

# -----------------------------
# Charger le dataset nettoyé
# -----------------------------
df = pd.read_csv("dataset_irrigation_clean.csv")

# -----------------------------
# Encodage du 5ème paramètre (Type de culture)
# -----------------------------
# On transforme 'Riz', 'Café', etc., en 0, 1, 2...
le_crop = LabelEncoder()
df['crop_type_encoded'] = le_crop.fit_transform(df['crop_type'])

# -----------------------------
# Sélection des 5 paramètres essentiels
# -----------------------------
# Ajout de 'crop_type_encoded' comme 5ème paramètre
features = ["N", "P", "K", "temperature", "crop_type_encoded"]
target = "water_usage_efficiency"

X = df[features]
y = df[target]

# -----------------------------
# Séparation train / test
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------------
# Entraînement du modèle
# -----------------------------
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# -----------------------------
# Sauvegarde du modèle et de l'encodeur
# -----------------------------
# On sauvegarde aussi l'encodeur pour pouvoir réutiliser le modèle plus tard
with open("water_model.pkl", "wb") as f:
    pickle.dump({'model': model, 'encoder': le_crop}, f)

print("✅ Modèle avec 5 paramètres entraîné et sauvegardé : water_model.pkl")