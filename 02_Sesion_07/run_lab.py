import sqlite3
import os

DB_PATH = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\Novamarket_SO7_Danna.db"

def print_table(title, cursor, rows, col_width=16):
    cols = [desc[0] for desc in cursor.description]
    sep = "+" + "+".join(["-" * (col_width + 2) for _ in cols]) + "+"
    header = "| " + " | ".join(str(c).ljust(col_width) for c in cols) + " |"
    print(f"\n{'═'*70}")
    print(f"  {title}")
    print(f"{'═'*70}")
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v if v is not None else 'NULL').ljust(col_width) for v in row) + " |")
    print(sep)
    print(f"  ➜ {len(rows)} fila(s) retornadas\n")

def run(con, title, sql):
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    print_table(title, cur, rows)
    return rows

con = sqlite3.connect(DB_PATH)
print(f"\n✅ Conectado a: {os.path.basename(DB_PATH)}\n")

# ── VERIFICACIÓN INICIAL ─────────────────────────────────────────────────────
run(con, "VERIFICACIÓN INICIAL — Registros por tabla", """
SELECT 'DimProducto' AS Tabla, COUNT(*) AS Registros FROM DimProducto
UNION ALL SELECT 'DimCiudad',  COUNT(*) FROM DimCiudad
UNION ALL SELECT 'DimFecha',   COUNT(*) FROM DimFecha
UNION ALL SELECT 'FactVentas', COUNT(*) FROM FactVentas
""")

# ── BLOQUE A ─────────────────────────────────────────────────────────────────
run(con, "A1 — Primeras 10 transacciones de FactVentas", """
SELECT * FROM FactVentas LIMIT 10
""")

run(con, "A2 — Total de registros en FactVentas", """
SELECT COUNT(*) AS Total_Transacciones FROM FactVentas
""")

run(con, "A3 — Diccionario de productos con margen", """
SELECT
    Nombre AS Producto,
    Categoria,
    Precio_Unitario,
    Costo_Unitario,
    (Precio_Unitario - Costo_Unitario)             AS Margen_Bruto,
    ROUND((Precio_Unitario - Costo_Unitario)
          / Precio_Unitario * 100, 1)              AS Margen_Pct
FROM DimProducto
ORDER BY Margen_Pct DESC
""")

# ── BLOQUE B ─────────────────────────────────────────────────────────────────
run(con, "B1 — Columnas seleccionadas de FactVentas", """
SELECT TransaccionID, FechaID, Cantidad, Precio_Venta
FROM FactVentas
LIMIT 15
""")

run(con, "B2 — Venta_Bruta y Venta_Neta calculadas", """
SELECT
    TransaccionID,
    CiudadID,
    Cantidad,
    Precio_Venta,
    Descuento_Pct,
    ROUND(Precio_Venta * Cantidad, 2)                            AS Venta_Bruta,
    ROUND(Precio_Venta * Cantidad * Descuento_Pct, 2)           AS Descuento_Monto,
    ROUND(Precio_Venta * Cantidad * (1 - Descuento_Pct), 2)     AS Venta_Neta
FROM FactVentas
LIMIT 20
""")

# ── BLOQUE C ─────────────────────────────────────────────────────────────────
run(con, "C1 — Ventas en Leticia (CiudadID=6)  [Éxito: 76 filas]", """
SELECT COUNT(*) AS Transacciones_Leticia FROM FactVentas WHERE CiudadID = 6
""")

run(con, "C2 — Descuento > 15%  [Éxito: 46 filas]", """
SELECT TransaccionID, FechaID, CiudadID, Descuento_Pct,
       ROUND(Precio_Venta * Cantidad * (1 - Descuento_Pct), 2) AS Venta_Neta
FROM FactVentas
WHERE Descuento_Pct > 0.15
ORDER BY Descuento_Pct DESC
""")

run(con, "C3 — Leticia CON descuento (AND)  [Éxito: 38 filas]", """
SELECT COUNT(*) AS Leticia_Con_Descuento FROM FactVentas
WHERE CiudadID = 6 AND Descuento_Pct > 0
""")

run(con, "C4 — Ciudades del Caribe IN(4,5)  [Éxito: 154 filas]", """
SELECT COUNT(*) AS Ventas_Caribe FROM FactVentas
WHERE CiudadID IN (4, 5)
""")

run(con, "C5 — Ventas Noviembre 2023  [Éxito: 155 filas]", """
SELECT COUNT(*) AS Ventas_Noviembre FROM FactVentas
WHERE FechaID BETWEEN 20231101 AND 20231130
""")

run(con, "C6 — Categorías que empiezan con 'S'  [Éxito: 2 filas]", """
SELECT Nombre, Categoria FROM DimProducto
WHERE Categoria LIKE 'S%'
""")

run(con, "C7 — Fechas sin NombreMes (IS NULL)  [Éxito: 0 filas]", """
SELECT COUNT(*) AS Fechas_Sin_Mes FROM DimFecha
WHERE NombreMes IS NULL
""")

# ── BLOQUE D ─────────────────────────────────────────────────────────────────
run(con, "D1 — Top 10 mayor Costo_Envio", """
SELECT TransaccionID, CiudadID, Costo_Envio, Precio_Venta, Cantidad
FROM FactVentas
ORDER BY Costo_Envio DESC
LIMIT 10
""")

run(con, "D2 — Top 10 peor margen (Venta_Neta - Costo_Envio)", """
SELECT
    TransaccionID, CiudadID, Precio_Venta, Cantidad, Descuento_Pct, Costo_Envio,
    ROUND(Precio_Venta * Cantidad * (1 - Descuento_Pct) - Costo_Envio, 2) AS Margen_Aproximado
FROM FactVentas
ORDER BY Margen_Aproximado ASC
LIMIT 10
""")

run(con, "D3 — Top 5 ventas de Leticia con mayor Costo_Envio", """
SELECT
    TransaccionID, FechaID, ProductoID, Cantidad,
    ROUND(Precio_Venta * Cantidad * (1 - Descuento_Pct), 2)              AS Venta_Neta,
    Costo_Envio,
    ROUND(Precio_Venta * Cantidad * (1 - Descuento_Pct) - Costo_Envio, 2) AS Margen_Aproximado
FROM FactVentas
WHERE CiudadID = 6
ORDER BY Costo_Envio DESC
LIMIT 5
""")

# ── BLOQUE E — ENTREGABLES ───────────────────────────────────────────────────
run(con, "E1 (Fácil) — Ventas Septiembre 2023  [Éxito: 153 filas]", """
SELECT COUNT(*) AS Ventas_Septiembre
FROM FactVentas
WHERE FechaID BETWEEN 20230901 AND 20230930
""")

run(con, "E2 (Medio) — Top 10 descuento fuera de Leticia", """
SELECT TransaccionID, CiudadID, Descuento_Pct, Precio_Venta
FROM FactVentas
WHERE CiudadID <> 6
ORDER BY Descuento_Pct DESC
LIMIT 10
""")

run(con, "E3 (Difícil) — Nov con desc>20% Y envio>500  [Éxito: 6 filas]", """
SELECT COUNT(*) AS Ventas_Destrozan_Valor
FROM FactVentas
WHERE FechaID BETWEEN 20231101 AND 20231130
  AND Descuento_Pct > 0.20
  AND Costo_Envio > 500
""")

con.close()
print("\n🎯 Laboratorio 07 completado exitosamente.\n")
