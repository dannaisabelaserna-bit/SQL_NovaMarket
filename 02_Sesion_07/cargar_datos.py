import pandas as pd
import sqlite3
import os

# Configuracion
EXCEL_FILE  = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\04_Ventas_Datos_Limpios_S03.xlsx"
DATABASE_FILE = r"d:\ACER\Downloads\SQL_NovaMarket-main (3)\SQL_NovaMarket-main\02_Sesion_07\Novamarket_SO7_Danna.db"

print("Iniciando carga desde:", EXCEL_FILE)

# ── 1. LEER EXCEL ────────────────────────────────────────────────────────────
df = pd.read_excel(EXCEL_FILE, sheet_name='Tabla1')
print("Columnas del Excel:", list(df.columns))
print("Filas cargadas:", len(df))

# ── 2. DimProducto ───────────────────────────────────────────────────────────
# Detectar columnas de producto
prod_cols = [c for c in df.columns if 'roduct' in c or 'Produc' in c]
cat_cols  = [c for c in df.columns if 'ategor' in c or 'Categ' in c]
prec_cols = [c for c in df.columns if 'recio' in c or 'Price' in c or 'Unit' in c]
cost_cols = [c for c in df.columns if 'osto' in c or 'Cost' in c]

print("Cols producto:", prod_cols)
print("Cols categoria:", cat_cols)
print("Cols precio:", prec_cols)
print("Cols costo:", cost_cols)

# Tomar la primera coincidencia de cada uno
col_prod = prod_cols[0] if prod_cols else None
col_cat  = cat_cols[0]  if cat_cols  else None
col_prec = prec_cols[0] if prec_cols else None
col_cost = cost_cols[0] if cost_cols else None

# Construir DimProducto
if col_prod:
    dim_prod_raw = df[[col_prod]].drop_duplicates().sort_values(col_prod).reset_index(drop=True)
    dim_producto = pd.DataFrame()
    dim_producto['ProductoID'] = range(1, len(dim_prod_raw) + 1)
    dim_producto['Nombre'] = dim_prod_raw[col_prod].values
    if col_cat:
        cat_map = df.groupby(col_prod)[col_cat].first()
        dim_producto['Categoria'] = dim_producto['Nombre'].map(cat_map)
    else:
        dim_producto['Categoria'] = 'General'
    if col_prec:
        prec_map = df.groupby(col_prod)[col_prec].mean()
        dim_producto['Precio_Unitario'] = dim_producto['Nombre'].map(prec_map).round(2)
    else:
        dim_producto['Precio_Unitario'] = 0
    if col_cost:
        cost_map = df.groupby(col_prod)[col_cost].mean()
        dim_producto['Costo_Unitario'] = dim_producto['Nombre'].map(cost_map).round(2)
    else:
        dim_producto['Costo_Unitario'] = 0
else:
    dim_producto = pd.DataFrame({'ProductoID':[1],'Nombre':['Producto'],'Categoria':['General'],'Precio_Unitario':[0],'Costo_Unitario':[0]})

print("\nDimProducto:")
print(dim_producto)

# ── 3. DimCiudad ─────────────────────────────────────────────────────────────
city_cols = [c for c in df.columns if 'iudad' in c or 'City' in c or 'Loc' in c or 'Region' in c]
print("Cols ciudad:", city_cols)
col_city = city_cols[0] if city_cols else None

regiones = {
    'Bogota':'Centro','Bogotá':'Centro',
    'Medellin':'Andina','Medellín':'Andina',
    'Cali':'Pacifico','Cali':'Pacifico',
    'Barranquilla':'Caribe','Cartagena':'Caribe',
    'Leticia':'Amazonia'
}
factor_envio = {
    'Bogota':1.0,'Bogotá':1.0,
    'Medellin':1.2,'Medellín':1.2,
    'Cali':1.3,
    'Barranquilla':1.5,'Cartagena':1.6,
    'Leticia':2.5
}
costo_base = {
    'Bogota':200,'Bogotá':200,
    'Medellin':250,'Medellín':250,
    'Cali':280,
    'Barranquilla':350,'Cartagena':380,
    'Leticia':650
}

if col_city:
    ciudades = sorted(df[col_city].dropna().unique())
    dim_ciudad = pd.DataFrame({'CiudadID': range(1, len(ciudades)+1), 'Nombre': ciudades})
    dim_ciudad['Region']         = dim_ciudad['Nombre'].map(regiones).fillna('Otro')
    dim_ciudad['Factor_Envio']   = dim_ciudad['Nombre'].map(factor_envio).fillna(1.0)
    dim_ciudad['Costo_Envio_Base'] = dim_ciudad['Nombre'].map(costo_base).fillna(200)
else:
    dim_ciudad = pd.DataFrame({'CiudadID':[1],'Nombre':['Ciudad'],'Region':['Otro'],'Factor_Envio':[1.0],'Costo_Envio_Base':[200]})

print("\nDimCiudad:")
print(dim_ciudad)

# ── 4. DimFecha ──────────────────────────────────────────────────────────────
fecha_cols = [c for c in df.columns if 'echa' in c or 'Date' in c or 'date' in c]
print("Cols fecha:", fecha_cols)
col_fecha = fecha_cols[0] if fecha_cols else None

if col_fecha:
    fechas = pd.to_datetime(df[col_fecha].dropna().unique())
    fechas = pd.DatetimeIndex(sorted(fechas))
    dim_fecha = pd.DataFrame()
    dim_fecha['FechaID']    = fechas.strftime('%Y%m%d').astype(int)
    dim_fecha['Fecha']      = fechas.strftime('%Y-%m-%d')
    dim_fecha['Anio']       = fechas.year
    dim_fecha['Mes']        = fechas.month
    dim_fecha['NombreMes']  = fechas.strftime('%B')
    dim_fecha['Trimestre']  = fechas.quarter
    dim_fecha['DiaSemana']  = fechas.strftime('%A')
    dim_fecha['EsFinde']    = fechas.weekday.isin([5, 6]).astype(int)
    # Evento especial ejemplo (Black Friday 2023)
    dim_fecha['Evento_Especial'] = None
    bf_mask = dim_fecha['Fecha'] == '2023-11-24'
    dim_fecha.loc[bf_mask, 'Evento_Especial'] = 'Black Friday'
else:
    dim_fecha = pd.DataFrame({'FechaID':[20230901],'Fecha':['2023-09-01'],'Anio':[2023],'Mes':[9],'NombreMes':['September'],'Trimestre':[3],'DiaSemana':['Friday'],'EsFinde':[0],'Evento_Especial':[None]})

print(f"\nDimFecha: {len(dim_fecha)} fechas unicas")

# ── 5. FactVentas ────────────────────────────────────────────────────────────
fact = df.copy()

# Mapear ProductoID
if col_prod:
    prod_map = dict(zip(dim_producto['Nombre'], dim_producto['ProductoID']))
    fact['ProductoID'] = fact[col_prod].map(prod_map)

# Mapear CiudadID
if col_city:
    city_map = dict(zip(dim_ciudad['Nombre'], dim_ciudad['CiudadID']))
    fact['CiudadID'] = fact[col_city].map(city_map)

# FechaID
if col_fecha:
    fact['FechaID'] = pd.to_datetime(fact[col_fecha]).dt.strftime('%Y%m%d').astype(int)

# Detectar columnas de transaccion
id_cols   = [c for c in df.columns if 'ID' in c or 'id' in c or 'Trans' in c]
cant_cols = [c for c in df.columns if 'antid' in c or 'Cant' in c or 'Qty' in c or 'Qua' in c]
desc_cols = [c for c in df.columns if 'escuen' in c or 'Disc' in c or 'desc' in c.lower()]
env_cols  = [c for c in df.columns if 'nvio' in c or 'Ship' in c or 'ship' in c or 'Envio' in c or 'Envío' in c]

print("Cols id:", id_cols)
print("Cols cantidad:", cant_cols)
print("Cols descuento:", desc_cols)
print("Cols envio:", env_cols)

col_id   = id_cols[0]   if id_cols   else None
col_cant = cant_cols[0] if cant_cols else None
col_desc = desc_cols[0] if desc_cols else None
col_env  = env_cols[0]  if env_cols  else None

fact_ventas = pd.DataFrame()
fact_ventas['TransaccionID'] = fact[col_id].values   if col_id   else range(1, len(fact)+1)
fact_ventas['FechaID']       = fact['FechaID'].values if col_fecha else 20230901
fact_ventas['ProductoID']    = fact['ProductoID'].values if col_prod else 1
fact_ventas['CiudadID']      = fact['CiudadID'].values if col_city else 1
fact_ventas['Cantidad']      = fact[col_cant].values  if col_cant  else 1
fact_ventas['Precio_Venta']  = fact[col_prec].values  if col_prec  else 0
fact_ventas['Descuento_Pct'] = fact[col_desc].values  if col_desc  else 0
fact_ventas['Costo_Envio']   = fact[col_env].values   if col_env   else 0

print(f"\nFactVentas: {len(fact_ventas)} filas")

# ── 6. GUARDAR EN SQLITE ─────────────────────────────────────────────────────

conn = sqlite3.connect(DATABASE_FILE)
dim_producto.to_sql('DimProducto', conn, if_exists='replace', index=False)
dim_ciudad.to_sql('DimCiudad',     conn, if_exists='replace', index=False)
dim_fecha.to_sql('DimFecha',       conn, if_exists='replace', index=False)
fact_ventas.to_sql('FactVentas',   conn, if_exists='replace', index=False)
conn.close()

print(f"\nBase de Datos '{os.path.basename(DATABASE_FILE)}' creada con exito!")
print(f"  DimProducto : {len(dim_producto)} filas")
print(f"  DimCiudad   : {len(dim_ciudad)} filas")
print(f"  DimFecha    : {len(dim_fecha)} filas")
print(f"  FactVentas  : {len(fact_ventas)} filas")
