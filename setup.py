import sqlite3
import json
import csv
import sqlite3
import yfinance
import requests
import os
import shutil

SAVE_DIR = "data/logo"
SOURCE = "static/assets/anonymous.png"

with open("config.json", "r") as f:
    config = json.load(f)

googlepass = config["googlepass"]
logo = config["logo.dev"]
secret = config["app-secret"]
with open(".env", "w") as f:
    f.write(f"SECRET={secret}\n" + f"APP={googlepass}\n" + f"LOGO={logo}")

csv_file = 'data/NASDAQ/Ticker.csv'

conn = sqlite3.connect('databases/stocks.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS STOCKS (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Tickers TEXT NOT NULL
    )
''')

with open(csv_file, 'r', newline='') as file:
    reader = csv.reader(file)
    
    next(reader, None)
    
    for row in reader:
        if row: 
            
            ticker = row[0]
            try:
                tickered = yfinance.Ticker(ticker)
                try:
                    domain = tickered.info.get("website").replace("https://", "").replace("http://", "").split("/")[0]
                except:
                    domain = "https://cdn-icons-png.flaticon.com/128/149/149071.png"
                url = f"https://img.logo.dev/{domain}?token={logo}"
                response = requests.get(url)
                directory = os.path.dirname(f"data/logo/{ticker}")
                os.makedirs(directory, exist_ok=True)
                if response.status_code == 200:
                    with open(os.path.join(SAVE_DIR, f"{ticker}.png"), "wb") as f:
                        f.write(response.content)
                    print(f"✅ Image saved! for {ticker}")
                elif response.status_code == 404:
                        shutil.copyfile(SOURCE, f"data/logo/{ticker}.png")
                else:
                    print("❌ Failed to download image.")

                cursor.execute("INSERT INTO STOCKS (Tickers) VALUES (?)", (ticker,))
                

            except ValueError:
                pass
            
    conn.commit()
    conn.close()


conn = sqlite3.connect("databases/users.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE "USERS" (
	"Username"	TEXT,
	"Password"	TEXT,
    "Email"  TEXT
)
''')

conn.commit()
conn.close()
