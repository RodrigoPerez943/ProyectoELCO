import sqlite3
import os

# Definir la ruta del archivo de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "mediciones.db")

# Conectar a la base de datos
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Verificar si la tabla `mediciones` existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mediciones';")
if cursor.fetchone():
    print("✅ La tabla 'mediciones' existe.")
else:
    print("❌ ERROR: La tabla 'mediciones' NO existe.")
    conn.close()
    exit()

# Verificar si hay nodos registrados
cursor.execute("SELECT DISTINCT node_id FROM mediciones;")
nodos = cursor.fetchall()

if nodos:
    print("✅ Nodos encontrados:", nodos)
else:
    print("⚠️ No hay nodos registrados en la base de datos.")

# Mostrar contenido completo de la tabla `mediciones`
cursor.execute("SELECT * FROM mediciones ORDER BY timestamp DESC LIMIT 10;")  # Últimas 10 mediciones
datos = cursor.fetchall()

if datos:
    print("\n📊 Últimos 10 registros en la base de datos:")
    for row in datos:
        print(row)
else:
    print("⚠️ No hay mediciones registradas en la base de datos.")

# Cerrar conexión
conn.close()
