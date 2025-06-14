import sqlite3
import json
import csv
import sqlite3

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
            cursor.execute("INSERT INTO STOCKS (Tickers) VALUES (?)", (ticker,))


conn.commit()
conn.close()



with open("config.json", "r") as f:
    config = json.load(f)

googlepass = config["googlepass"]
logo = config["logo.dev"]
with open(".env", "w") as f:
    f.write("SECRET=Calibrisa\n" + f"APP={googlepass}\n" + f"LOGO={logo}")

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
