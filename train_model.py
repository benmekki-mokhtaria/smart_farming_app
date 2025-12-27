import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# -----------------------------
# Charger le dataset nettoyé
# -----------------------------
df = pd.read_csv("dataset_irrigation_clean.csv")

# -----------------------------
# Sélection paramètres essentiels
# -----------------------------
features = ["N", "P", "K", "temperature"]
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
# Sauvegarde du modèle
# -----------------------------
with open("water_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Modèle entraîné et sauvegardé avec succès : water_model.pkl")
