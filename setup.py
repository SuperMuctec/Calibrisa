import sqlite3

with open(".env", "w") as f:
    f.write("SECRET=Calibrisa")
    

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
