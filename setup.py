import sqlite3
import json

with open("config.json", "r") as f:
    config = json.load(f)

googlepass = config["googlepass"]
logo = config["logo.dev"]

with open(".env", "w") as f:
    f.write("SECRET=Calibrisa")
    f.append(f"APP={googlepass}")
    f.append(f"LOGO={logo}")

conn = sqlite3.connect("databases/users.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE "USERS" (
	"Username"	TEXT,
	"Password"	TEXT
)
''')

conn.commit()
conn.close()
