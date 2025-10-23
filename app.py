from flask import Flask, flash, redirect, render_template, request, session, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # TODO: Ändra detta till en slumpmässig hemlig nyckel

# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Ändra detta till ditt MySQL-användarnamn
    'password': '',  # Ändra detta till ditt MySQL-lösenord
    'database': 'inlamning_1'  # TODO: Ändra detta till ditt databasnamn
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
    
        # Trimma indata för att undvika extra mellanslag
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500

        try:
            cursor = connection.cursor(dictionary=True)

            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            # Debug-utskrift (ta bort eller begränsa i produktion)
            print(f"Login attempt: username={username!r}, user_found={bool(user)}")

            if not user:
                # Användaren finns inte
                return render_template('login.html', error='Ogiltigt användarnamn eller lösenord'), 401

            # Jämför lösenord (OBS: använd hash i produktion!)
            if user.get('password') == password:
                session['user_id'] = user.get('id')
                session['username'] = user.get('username')
                flash('Inloggning lyckades!')
                return render_template('index.html', user=user)
            else:
                flash('Ogiltigt användarnamn eller lösenord')
                # Lösenord fel
                return render_template('login.html'), 401

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return render_template('login.html')

@app.route('/log_out')
def log_out():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)