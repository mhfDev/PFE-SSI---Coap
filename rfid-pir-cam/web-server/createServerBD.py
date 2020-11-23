import sqlite3

con = sqlite3.connect("sensordata.db")
c = con.cursor()
c.execute("CREATE TABLE rfid_readings (id INTEGER PRIMARY KEY AUTOINCREMENT, UID TEXT, STATUS INTEGER, currentdate DATE, currentime TIME)")
con.commit()
c.close()