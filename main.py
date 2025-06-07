from flask import *
from datetime import datetime
import random
import dotenv
import os
import sqlite3
from flask_session import Session
import smtplib

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


dotenv.load_dotenv()
key = os.getenv('SECRET')
app.secret_key = key
Session(app)

@app.errorhandler(404)
def not_found(e):
  # defining function
  return render_template("Errors/Error-404.html")

@app.route("/")
def home():

    try:
        session["name"] = session["name"]
        reuter = session["name"]
    except:
        reuter = None
    cards = [
        {
            "title": "Practice",
            "description": "Provide you practice so that you can flex or win at the big place",
            "tags": [
                { "label": "Practice", "bg": "bg-green-100", "text": "text-red-700" },
                { "label": "Play", "bg": "bg-blue-100", "text": "text-yellow-700" },
            ],
        },
        {
            "title": "Compete",
            "description": "Compete with other players to win big.",
            "tags": [
                { "label": "Community", "bg": "bg-blue-100", "text": "text-blue-700" },
                { "label": "Compete", "bg": "bg-cyan-100", "text": "text-fuchsia-700" },
                { "label": "Leaderboard", "bg": "bg-fuchsia-100", "text": "text-fuchsia-700" },
            ],
        }
    ]
    current_year = datetime.now().year
    return render_template("Home.html", current_year=current_year, cards=cards, nb="Calibrisa", user=reuter)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("databases/users.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM USERS WHERE Username = ?", (username,))
        result = cur.fetchone()

        if result:
            flash("Username already exists! Please choose another.")
            return redirect(url_for('register'))
        else:
            cur.execute("INSERT INTO USERS (Username, Password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash("Registration successful! You can now log in.")
            return redirect(url_for('register'))
        
    return render_template("Register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("databases/users.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM USERS WHERE Username = ?", (username,))
        result = cur.fetchone()
        db_username = result[0]
        db_password = result[1]
        if result:
            if username == db_username and password == db_password:
                session["name"] = username
                print(session)
                return redirect(url_for('home'))
            else:
                flash("Your Password is wrong")
                return redirect(url_for('login'))
        else:
            flash("Username does not exist! Please register by clicking on this popup.")
            return redirect(url_for('login'))
    return render_template("Login.html")

@app.route("/logout")
def logout():
    try:
        session["name"] = None
    except:
        pass
    return redirect(url_for('home'))

app.run(debug=True)