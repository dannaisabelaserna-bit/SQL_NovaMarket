import sqlite3
import os
import re

DB_PATH = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\Novamarket_SO7_Danna.db"
SQL_FILE = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\06_Laboratorio_Consultas.sql"

def print_table(cursor, rows, col_width=16):
    if not cursor.description:
        return
    cols = [desc[0] for desc in cursor.description]
    sep = "+" + "+".join(["-" * (col_width + 2) for _ in cols]) + "+"
    header = "| " + " | ".join(str(c)[:col_width].ljust(col_width) for c in cols) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v if v is not None else 'NULL')[:col_width].ljust(col_width) for v in row) + " |")
    print(sep)
    print(f"  ➜ {len(rows)} fila(s) retornadas\n")

print(f"\n✅ Conectado a: {os.path.basename(DB_PATH)}\n")
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

with open(SQL_FILE, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Eliminar comentarios de una linea
sql_script = re.sub(r'--.*', '', sql_script)

# Separar consultas por punto y coma
queries = [q.strip() for q in sql_script.split(';') if q.strip()]

for i, query in enumerate(queries, 1):
    print(f"{'═'*70}")
    print(f"  EJECUCIÓN #{i}")
    print(f"{'═'*70}")
    print(f"{query[:150]}...\n")
    try:
        cur.execute(query)
        if query.upper().startswith("SELECT"):
            rows = cur.fetchall()
            print_table(cur, rows)
        else:
            con.commit()
            print("  ➜ Comando ejecutado con éxito.\n")
    except Exception as e:
        print(f"❌ Error al ejecutar: {e}\n")

con.close()
print("🎯 Ejecución de consultas completada.")
