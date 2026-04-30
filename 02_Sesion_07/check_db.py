import sqlite3
import os

db = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\Novamarket_SO7_Danna.db"
print("Tamano archivo:", os.path.getsize(db), "bytes")

con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT name, type FROM sqlite_master ORDER BY type, name")
rows = cur.fetchall()
print("Objetos en la BD:", rows)
con.close()
