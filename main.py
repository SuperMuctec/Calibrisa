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
import yfinance as yf
from jinja2 import *
from model import predict_stock_info

def has_website(ticker):
    try:
        info = yf.Ticker(ticker).info
        return bool(info.get("website"))
    except:
        return False


def get_company_description(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    return info.get("longBusinessSummary", "Description not available.")

def get_valuation_fundamentals(ticker: str) -> dict:
    info = yf.Ticker(ticker).info
    
    def safe_get(key, default="N/A"):
        return info.get(key, default)

    dividend_raw = safe_get("dividendYield")

    # Analyst rating isn't directly in yfinance.info — you'll need to fetch elsewhere or skip for now.
    try:
        return {
            "trailing_pe": safe_get("trailingPE"),
            "forward_pe": safe_get("forwardPE"),
            "eps_ttm": safe_get("trailingEps"),
            "eps_forward": safe_get("forwardEps"),
            "dividend_rate": safe_get("dividendRate"),
            "dividend_yield": float(dividend_raw),
            "analyst_rating": "Buy",  # Placeholder since yfinance doesn't give this directly
            "target_price": safe_get("targetMeanPrice")
        }
    except:
        return {
            "trailing_pe": safe_get("trailingPE"),
            "forward_pe": safe_get("forwardPE"),
            "eps_ttm": safe_get("trailingEps"),
            "eps_forward": safe_get("forwardEps"),
            "dividend_rate": safe_get("dividendRate"),
            "dividend_yield": "N/A",
            "analyst_rating": "Buy",  # Placeholder since yfinance doesn't give this directly
            "target_price": safe_get("targetMeanPrice")
        }

def get_dividend_yield(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    yield_percent = info.get("dividendYield")

    if yield_percent is None:
        return "N/A"

    return f"{float(yield_percent)}%"

def get_average_volume(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    volume = info.get("averageVolume")

    if volume is None:
        return "Volume not available"

    # Format large numbers
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return str(volume)

def get_market_cap(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    cap = info.get("marketCap")

    if cap is None:
        return "Market cap not available"

    # Format it to Billion/Trillion for human brains
    if cap >= 1_000_000_000_000:
        return f"${cap / 1_000_000_000_000:.2f}T"
    elif cap >= 1_000_000_000:
        return f"${cap / 1_000_000_000:.2f}B"
    elif cap >= 1_000_000:
        return f"${cap / 1_000_000:.2f}M"
    else:
        return f"${cap}"

def get_52_week_range(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    low = info.get("fiftyTwoWeekLow")
    high = info.get("fiftyTwoWeekHigh")

    if low is None or high is None:
        return "52-week range not available 🤷‍♂️"
    
    return f"${low} – ${high}"

def get_current_price(ticker: str) -> float:
    info = yf.Ticker(ticker).info
    return info.get("currentPrice", "Price not available 💸")

def get_company_field(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    sector = info.get("sector", "Unknown Sector")
    industry = info.get("industry", "Unknown Industry")
    return f"{sector} • {industry}"

def get_company_website(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    return info.get("website", "Website not found 🫠")

def get_company_name(ticker: str) -> str:
    info = yf.Ticker(ticker).info
    return info.get("longName") or info.get("shortName") or "Name not found 😵"

def save_stock_csv(ticker: str):
    """
    Downloads historical stock data (2020-2025) for the given ticker.
    Saves to '<TICKER>.csv' only if it doesn't already exist.
    """
    filename = f"Fata/csv/{ticker.upper()}.csv"

    if os.path.exists(filename):
        return

    try:
        data = yf.download(ticker, start="2020-01-01", end="2025-01-01", interval="1d")
        data.reset_index(inplace=True)
        data['Date'] = data['Date'].dt.strftime('%d-%m-%Y')
        data.to_csv(filename, index=False)
        print(f"✅ Saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving {ticker}: {e}")

def get_today_data(ticker: str) -> dict:
    data = yf.Ticker(ticker).history(period="1d", interval="1m")
    
    if data.empty:
        return {"error": "No data found or market is closed."}

    latest = data.iloc[-1]  # Get the last row
    result = {}

    for key, value in latest.items():
        if isinstance(value, float):
            result[key] = round(value, 2)
        else:
            result[key] = value

    return result

# Load config and environment variables
with open("config.json", "r") as f:
    config = json.load(f)

receiver_email = config["receiver_email"]

dotenv.load_dotenv(override=True)
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
print(google_password)
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

@app.route("/choose")
def choose():
    return render_template("Model/choose.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    ticker = request.form["ticker"].upper()
    date = request.form["date"]
    email = session.get("name")

    if not email:
        return "Unauthorized", 401 #CHANGE THIS PART TO RETURN UR 403 PAGE1

    result = predict_stock_info(ticker, date)
    print(result)

    if "error" in result:
        return result["error"], 400

    # Only add fallback values if not present in the ML model output
    result.setdefault("name", get_company_name(ticker))
    result.setdefault("field", get_company_field(ticker))
    result.setdefault("desc", get_company_description(ticker))
    result.setdefault("website", get_company_website(ticker))

    # Save path for the user's predicted report
    save_path = os.path.join("user_data", email, ticker, date)
    os.makedirs(save_path, exist_ok=True)

    # Render the HTML report with predictions
    html_content = render_template("Applet/Ticker_Data.html", **result)

    # Save HTML to file
    file_path = os.path.join(save_path, "report.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return redirect(url_for("view_report", email=email, ticker=ticker, date=date))


@app.route("/view/<email>/<ticker>/<date>")
def view_report(email, ticker, date):
    if session.get("name") != email:
        return "Access Denied", 403

    file_path = os.path.join("user_data", email, ticker, date, "report.html")
    if not os.path.exists(file_path):
        return "Report not found", 404

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@app.route("/analysis_dashboard")
def analysis_dashboard():
    email = session.get("name")
    base_dir = os.path.join("user_data", email)
    records = []

    for root, dirs, files in os.walk(base_dir):
        if "report.html" in files:
            parts = root.split(os.sep)
            try:
                user_email, ticker, date = parts[-3:]
                if user_email == email:
                    records.append({
                        "ticker": ticker,
                        "date": date,
                        "path": f"/view/{email}/{ticker}/{date}"
                    })
            except ValueError:
                continue

    records.sort(key=lambda r: r['date'], reverse=True)

    return render_template("Model/analysis_dashboard.html", records=records)


@app.route("/dashboard")
def index():
    query = request.args.get("q", "").lower()
    page = int(request.args.get("page", 1))
    per_page = 100

    conn = sqlite3.connect("databases/stocks.db")
    cur = conn.cursor()
    cur.execute("SELECT Tickers FROM STOCKS")
    results = cur.fetchall()
    conn.close()

    all_stocks = sorted(list(set([row[0] for row in results])))

    if query:
        filtered = [stock for stock in all_stocks if query in stock.lower()]
    else:
        filtered = all_stocks

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
        nb="Search Stocks",
        user=check_session(session)
    )



@app.route("/dashboard/<ticker>")
def stock_detail(ticker):
    info = get_today_data(ticker)
    website = get_company_website(ticker)
    name = get_company_name(ticker)
    field = get_company_field(ticker)
    price = get_current_price(ticker)
    week52range = get_52_week_range(ticker)
    market_cap = get_market_cap(ticker)
    avg_volume = get_average_volume(ticker)
    dividend = get_dividend_yield(ticker)
    valuation = get_valuation_fundamentals(ticker)
    desc = get_company_description(ticker)
    return render_template("Dashboard/Ticker_Data.html",desc=desc, ticker=ticker, nb=ticker, info = info, website = website, name = name, field = field, price=price, week=week52range, cap=market_cap, avg=avg_volume, dividend=dividend, valuation=valuation)

@app.route('/logo/<path:filename>')
def serve_logo(filename):
    return send_from_directory("data/logo", filename)
if __name__ == '__main__':
    app.run(debug=True)



