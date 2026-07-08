from flask import Flask, redirect, url_for, session, request, render_template
from routes import app as app_routes
import midtransclient
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()  # baca file .env

# Gunakan app dari routes.py
app = app_routes
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# === MIDTRANS CONFIG ===
snap = midtransclient.Snap(
    is_production=False,
    server_key=os.environ.get("MIDTRANS_SERVER_KEY"),
    client_key=os.environ.get("MIDTRANS_CLIENT_KEY")
)

# === GOOGLE AUTH CONFIG ===
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'consent'
    }
)

# === ROUTES ===
@app.route('/')
def index():
    user = session.get('user')
    return render_template('home_page.html', user=user)

@app.route('/google-login')
def google_login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo').json()
    except Exception as e:
        print("Google OAuth Error:", e)
        return redirect(url_for('index'))

    if not userinfo.get("email"):
        return "Gagal mendapatkan data user dari Google", 400

    # Simpan user di session
    session['user'] = userinfo
    session['email'] = userinfo.get('email')
    session['role'] = 'user'

    # Simpan ke database jika belum ada
    conn = sqlite3.connect('Trendify.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (userinfo['email'],))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute('''
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', (
            userinfo.get('name'),
            userinfo.get('email'),
            '-',  # password kosong (OAuth)
            'user'
        ))
        conn.commit()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)