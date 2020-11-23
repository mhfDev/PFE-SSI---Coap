import sqlite3

con = sqlite3.connect("imEtudiants.db")
c = con.cursor()
c.execute("CREATE TABLE etudiants (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, nom TEXT, prenom)")
c.execute("CREATE TABLE stats (id INTEGER PRIMARY KEY AUTOINCREMENT, current_date DATE, current_time TIME)")

con.commit()
c.close()