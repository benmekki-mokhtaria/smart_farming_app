import os, sqlite3, pickle, csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file

app = Flask(__name__)
app.secret_key = "smart_farming_expert_final_2025"

# --- 1. GESTION BASE DE DONNÉES (SQL) ---
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, n_val REAL, p_val REAL, k_val REAL, temperature REAL, result REAL, date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    if not conn.execute("SELECT * FROM users WHERE username='admin'").fetchone():
        conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

init_db()

# --- 2. CHARGEMENT DU MODÈLE IA ---
with open("models/model.pkl", "rb") as f:
    ml_data = pickle.load(f)

# --- 3. ROUTES AUTHENTIFICATION ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u, p = request.form.get("username"), request.form.get("password")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if user:
            session["user"] = u
            return redirect(url_for("index"))
        flash("Identifiants incorrects", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- 4. ACCUEIL ET ANALYSE IA ---
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session: return redirect(url_for("login"))
    prediction, analyse = None, {}
    
    if request.method == "POST":
        n, p, k, temp = float(request.form['n']), float(request.form['p']), float(request.form['k']), float(request.form['temp'])
        
        # Inférence avec le modèle IA
        df_input = pd.DataFrame([0]*len(ml_data['columns']), index=ml_data['columns']).T
        df_input['N'], df_input['P'], df_input['K'], df_input['temperature'] = n, p, k, temp
        prediction = ml_data['model'].predict(df_input)[0]

        # Analyse détaillée (Irrigation, Fertilisation, Gaspillage)
        analyse = {
            "irrigation": "Optimale (Humidité stable)" if temp < 30 and prediction > 3 else "Stress thermique : Augmenter l'apport en eau",
            "fertilisation": "Équilibrée" if n > 40 and p > 35 else "Carence détectée : Ajouter engrais Azoté/Phosphoré",
            "gaspillage": "Faible (Ressources bien utilisées)" if prediction > 3.8 else "Élevé : Plan inefficace, ajustez les doses",
            "n": n, "p": p, "k": k, "temp": temp
        }

        # Sauvegarde en base SQL
        conn = get_db()
        conn.execute("INSERT INTO predictions (n_val, p_val, k_val, temperature, result) VALUES (?, ?, ?, ?, ?)", (n,p,k,temp,prediction))
        conn.commit()
        conn.close()
        flash("Analyse générée avec succès !", "success")
        return render_template("index.html", prediction=prediction, analyse=analyse)

    return render_template("index.html")

# --- 5. HISTORIQUE & DASHBOARD ---
@app.route("/historique")
def historique():
    if "user" not in session: return redirect(url_for("login"))
    conn = get_db()
    data = conn.execute("SELECT * FROM predictions ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("historique.html", data=data)

@app.route("/export")
def export_csv():
    conn = get_db()
    cursor = conn.execute("SELECT * FROM predictions")
    file_path = "static/historique_smart_farming.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Azote', 'Phosphore', 'Potassium', 'Température', 'Score_IA', 'Date'])
        writer.writerows(cursor.fetchall())
    conn.close()
    return send_file(file_path, as_attachment=True)

# --- 6. GESTION UTILISATEURS (CRUD) ---
@app.route("/parametres")
def parametres():
    if "user" not in session: return redirect(url_for("login"))
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("parametres.html", users=users)

@app.route("/user/add", methods=["POST"])
def add_user():
    u, p = request.form.get("u"), request.form.get("p")
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        flash("Utilisateur ajouté !", "success")
    except: flash("Ce nom d'utilisateur existe déjà.", "danger")
    conn.close()
    return redirect(url_for("parametres"))

@app.route("/user/edit", methods=["POST"])
def edit_user():
    user_id, new_p = request.form.get("id"), request.form.get("new_p")
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE id=?", (new_p, user_id))
    conn.commit()
    conn.close()
    flash("Mot de passe mis à jour.", "info")
    return redirect(url_for("parametres"))

@app.route("/user/delete/<int:id>")
def delete_user(id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Utilisateur supprimé.", "warning")
    return redirect(url_for("parametres"))

if __name__ == "__main__":
    app.run(debug=True)