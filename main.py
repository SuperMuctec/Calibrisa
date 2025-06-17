from flask import *
from datetime import datetime
import dotenv
import os
import sqlite3
from flask_session import Session
import smtplib
import json
from email.message import EmailMessage
import random
import bcrypt

# Load config and environment variables
with open("config.json", "r") as f:
    config = json.load(f)

receiver_email = config["receiver_email"]

dotenv.load_dotenv()
key = os.getenv('SECRET')
google_password = os.getenv("APP")
salt = bcrypt.gensalt()

# Flask setup
app = Flask(__name__)
app.secret_key = key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Email settings
SENDER_EMAIL = "calibrisa.official@gmail.com"
SENDER_PASSWORD = google_password

# OTP Email sender
def send_otp_email(recipient_email, otp):
    msg = EmailMessage()
    msg['Subject'] = "Your OTP Code"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(f"Your OTP is: {otp}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email failed:", e)
        return False

# Error page
@app.errorhandler(404)
def not_found(e):
    return render_template("Errors/Error-404.html")

# Check session


def check_session(session):
    try:
        return session["name"]
    except:
        return None

# Home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        subject = request.form.get("subject")
        content = request.form.get("message")

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(SENDER_EMAIL, google_password)

                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = SENDER_EMAIL
                msg['To'] = receiver_email
                msg.set_content(f"\n From {name} through Calibrisa: Stock Analyzer\n\nMessage:\n{content}")

                smtp.send_message(msg)

            flash("Sending email successful")
        except Exception as e:
            print(e)
            flash("An error occurred, check console for more")

    user = check_session(session)
    cards = [
        {
            "title": "Practice",
            "description": "Provide you practice so that you can flex or win at the big place",
            "tags": [
                {"label": "Practice", "bg": "bg-green-100", "text": "text-red-700"},
                {"label": "Play", "bg": "bg-blue-100", "text": "text-yellow-700"},
            ],
        },
        {
            "title": "Compete",
            "description": "Compete with other players to win big.",
            "tags": [
                {"label": "Community", "bg": "bg-blue-100", "text": "text-blue-700"},
                {"label": "Compete", "bg": "bg-cyan-100", "text": "text-fuchsia-700"},
                {"label": "Leaderboard", "bg": "bg-fuchsia-100", "text": "text-fuchsia-700"},
            ],
        }
    ]
    return render_template("Home.html", current_year=datetime.now().year, cards=cards, nb="Calibrisa", user=user)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        otp_input = ''.join([request.form.get(f"otp{i}", "") for i in range(4)])

        # If we're verifying OTP
        if 'otp' in session and 'attempts' in session and session.get("otp"):
            if otp_input == session['otp']:
                conn = sqlite3.connect("databases/users.db")
                cur = conn.cursor()
                p = session["password"].encode()
                hashed = bcrypt.hashpw(p, salt)
                cur.execute("INSERT INTO USERS (Username, Password, Email) VALUES (?, ?, ?)",
                            (session['username'], hashed, session['email']))
                conn.commit()
                conn.close()
                session.pop('otp', None)
                session.pop('attempts', None)
                session.pop('username', None)
                session.pop('password', None)
                session.pop('email', None)
                flash("🎉 Registration successful!", "success")
                return redirect(url_for('register'))
            else:
                session['attempts'] -= 1
                if session['attempts'] <= 0:
                    flash("Access Denied: Wrong OTP", "danger")
                    session.pop('otp', None)
                    session.pop('attempts', None)
                else:
                    flash(f"Incorrect OTP. {session['attempts']} tries left.", "danger")
                return render_template("Register.html", show_otp=True,
                                       username=session.get('username', ''),
                                       email=session.get('email', ''))

        # Before sending OTP, check if user exists
        conn = sqlite3.connect("databases/users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM USERS WHERE Username = ? OR Email = ?", (username, email))
        existing_user = cur.fetchone()
        conn.close()

        if existing_user:
            flash("Username or Email already exists", "login")
            return render_template("Register.html", username=username, email=email)

        # If user does not exist, generate and send OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        session['otp'] = otp
        session['attempts'] = 3
        session['username'] = username
        session['email'] = email
        session['password'] = password  # temporarily storing until OTP is confirmed

        send_otp_email(email, otp)
        flash("OTP sent to your email.", "info")
        return render_template("Register.html", show_otp=True, username=username, email=email, password=password)

    # On GET request, clean session
    session.pop('otp', None)
    session.pop('attempts', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('password', None)
    return render_template("Register.html")



# Resend OTP
@app.route("/resend_otp", methods=["POST"])
def resend_otp():
    username = session.get("username")
    email = session.get("email")

    if not username or not email:
        flash("Session expired. Please fill the form again.", "danger")
        return redirect(url_for("register"))

    otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    session['otp'] = otp
    session['attempts'] = 3

    if send_otp_email(email, otp):
        flash("OTP resent!", "info")
    else:
        flash("Could not resend OTP. Try again.", "danger")
    return redirect(url_for("register"))

# Login route
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("databases/users.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM USERS WHERE Email = ?", (username,))
        result = cur.fetchone()

        if result:
            db_username = result[2]
            db_password = result[1]
            if username == db_username and bcrypt.checkpw(password.encode(), db_password):
                session["name"] = result[0]
                return redirect(url_for('home'))
            else:
                flash("Your Password is wrong")
                return redirect(url_for('login'))
        else:
            flash("Email does not exist! Please register.")
            return redirect(url_for('login'))
    return render_template("Login.html")

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect(url_for('home'))

def get_all_tickers():
    conn = sqlite3.connect("databases/stocks.db")
    cur = conn.cursor()
    cur.execute("SELECT Tickers FROM STOCKS")
    results = cur.fetchall()
    conn.close()
    return [row[0] for row in results]

@app.route("/dashboard")
def index():
    # Get query and page from request
    query = request.args.get("q", "").lower()
    page = int(request.args.get("page", 1))
    per_page = 100

    # Fetch all tickers
    conn = sqlite3.connect("databases/stocks.db")
    cur = conn.cursor()
    cur.execute("SELECT Tickers FROM STOCKS")
    results = cur.fetchall()
    conn.close()

    all_stocks = [row[0] for row in results]

    # Filter based on query
    if query:
        filtered = [stock for stock in all_stocks if query in stock.lower()]
    else:
        filtered = all_stocks

    # Pagination
    total_items = len(filtered)
    total_pages = (total_items + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = filtered[start:end]

    has_more = page < total_pages
    has_prev = page > 1

    return render_template(
        "Dashboard/dashboard.html",
        results=paginated_results,
        query=query,
        page=page,
        total_pages=total_pages,
        has_more=has_more,
        has_prev=has_prev,
        nb="Search Stocks"
    )


@app.route("/dashboard/<ticker>")
def stock_detail(ticker):
    return f"<h1>Welcome to the stock detail page for {ticker}</h1>"

@app.route('/logo/<path:filename>')
def serve_logo(filename):
    return send_from_directory("data/logo", filename)
if __name__ == '__main__':
    app.run(debug=True)

