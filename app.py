import sqlite3
import pickle
import os
import io
import csv
from flask import Flask, render_template, request, g, redirect, session, url_for, flash, Response

app = Flask(__name__)
app.secret_key = 'smart_agriculture_secret_key'
DATABASE = 'database.db'

# --- GESTION BASE DE DONNÉES ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, n_val REAL, p_val REAL, k_val REAL, temperature REAL, crop_type TEXT, result REAL, date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
        
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")
        conn.commit()

# --- CHARGEMENT IA ---
try:
    if os.path.exists("models/model.pkl"):
        with open("models/model.pkl", "rb") as f:
            ml_data = pickle.load(f)
        model = ml_data['model'] if isinstance(ml_data, dict) else ml_data
    else:
        model = None
except:
    model = None

with app.app_context():
    init_db()

# --- ROUTES AUTHENTIFICATION ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p)).fetchone()
        if user:
            session['user'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Identifiants incorrects", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- ROUTES PRINCIPALES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session: return redirect(url_for('login'))
    prediction, analyse = None, None
    if request.method == "POST":
        n = float(request.form.get('n', 0))
        p = float(request.form.get('p', 0))
        k = float(request.form.get('k', 0))
        temp = float(request.form.get('temp', 0))
        crop = request.form.get('crop_type', 'Riz')
        
        prediction = round(((n + p + k) / 300) * 5, 2)
        if prediction > 5: prediction = 4.80

        analyse = {
            'crop': crop, 'n': n, 'p': p, 'k': k, 'temp': temp,
            'irrigation': "Optimale" if prediction > 3.5 else "Standard",
            'fertilisation': "Riche" if n > 40 else "À surveiller",
            'gaspillage': "Faible" if prediction > 3 else "Modéré"
        }
        db = get_db()
        db.execute("INSERT INTO predictions (n_val, p_val, k_val, temperature, crop_type, result) VALUES (?,?,?,?,?,?)", (n, p, k, temp, crop, prediction))
        db.commit()
    return render_template('index.html', prediction=prediction, analyse=analyse)

@app.route('/historique')
def historique():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    data = db.execute("SELECT * FROM predictions ORDER BY date_creation DESC").fetchall()
    total = len(data)
    avg = sum(row['result'] for row in data) / total if total > 0 else 0
    return render_template('historique.html', data=data, total=total, avg_score=round(avg, 2))

# --- ROUTE EXPORT CSV ---
@app.route('/export/csv')
def export_csv():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    data = db.execute("SELECT crop_type, n_val, p_val, k_val, result, date_creation FROM predictions ORDER BY date_creation DESC").fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Culture', 'N', 'P', 'K', 'Score IA', 'Date'])
    for row in data:
        writer.writerow([row['crop_type'], row['n_val'], row['p_val'], row['k_val'], row['result'], row['date_creation']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=historique_smart_farming.csv"}
    )

@app.route('/settings')
def settings():
    if 'user' not in session: return redirect(url_for('login'))
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template('parametres.html', users=users)

@app.route('/user/add', methods=['POST'])
def add_user():
    db = get_db()
    db.execute("INSERT INTO users (username, password) VALUES (?,?)", (request.form.get('u'), request.form.get('p')))
    db.commit()
    return redirect(url_for('settings'))

@app.route('/user/delete/<int:id>')
def delete_user(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    return redirect(url_for('settings'))

if __name__ == '__main__':
    app.run(debug=True)