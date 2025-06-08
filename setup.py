import sqlite3
import json

with open("config.json", "r") as f:
    config = json.load(f)

receiver_email = config["googlepass"]

with open(".env", "w") as f:
    f.write("SECRET=Calibrisa")
    f.append("APP=your\ google\ app\ password")

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
