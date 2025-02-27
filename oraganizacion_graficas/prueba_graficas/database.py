import sqlite3
import os

# Ruta de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "mediciones.db")

def conectar_db():
    """Conectar a la base de datos SQLite"""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"⚠️ Error al conectar a la base de datos: {e}")
        return None

def inicializar_db():
    """ Crea la tabla si no existe """
    conn= conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            node_id INTEGER NOT NULL,
            temperature REAL,
            humidity REAL,
            pressure REAL
        )
    ''')
    conn.commit()
    conn.close()

def insertar_medicion(timestamp, node_id, temperature, humidity, pressure):
    """ Inserta una nueva medición en la base de datos """
    conn, cursor = conectar_db()
    cursor.execute('''
        INSERT INTO mediciones (timestamp, node_id, temperature, humidity, pressure)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, node_id, temperature, humidity, pressure))
    conn.commit()
    conn.close()

def obtener_mediciones_por_nodo(node_id):
    """Obtiene las mediciones de un nodo en la base de datos"""
    conn = conectar_db()
    
    # Verificar si la conexión se estableció correctamente
    if conn is None:
        print("⚠️ Error: No se pudo conectar a la base de datos.")
        return None, None, []  # Retorna lista vacía en caso de error

    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT timestamp, temperature, humidity, pressure
            FROM mediciones
            WHERE node_id = ?
        ''', (node_id,))

        datos = cursor.fetchall()

        print(f"✅ Se obtuvieron {len(datos)} mediciones para el nodo {node_id}.")
        return conn, cursor, datos  # Devuelve siempre 3 valores

    except sqlite3.Error as e:
        print(f"⚠️ Error al obtener datos del nodo {node_id}: {e}")
        return conn, cursor, []  # Retorna lista vacía en caso de error

# Inicializar la base de datos al ejecutar este script
if __name__ == "__main__":
    inicializar_db()
