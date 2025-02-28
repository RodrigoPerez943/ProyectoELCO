import sqlite3
import os
from flask_socketio import SocketIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "mediciones.db")

def conectar_db():
    """Conectar a la base de datos SQLite y devolver solo la conexión"""
    conn = sqlite3.connect(DB_FILE)
    return conn  # Solo devuelve la conexión

def crear_tabla():
    """Crea la tabla de mediciones si no existe"""
    conn = conectar_db()
    cursor = conn.cursor()  # Crear el cursor aquí

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            pressure REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def inicializar_db():
    """Crea la base de datos y la tabla de mediciones si no existen"""
    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            pressure REAL NOT NULL,
            ext REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def insertar_medicion(timestamp, node_id, temperature, humidity, pressure, ext):
    """Inserta una medición en la base de datos"""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO mediciones (timestamp, node_id, temperature, humidity, pressure, ext)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, node_id, temperature, humidity, pressure, ext))

    conn.commit()
    conn.close()
    # 🔴 Notificar a los clientes de la nueva medición
    #SocketIO.emit('nueva_medicion', {"nodo_id": node_id})

def obtener_mediciones_por_nodo(node_id):
    """Obtiene las mediciones de un nodo en la base de datos"""
    conn = conectar_db()

    # Verificar si la conexión es válida
    if conn is None:
        print("⚠️ Error: No se pudo conectar a la base de datos.")
        return None, None, []  # Retornar valores por defecto para evitar errores

    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT timestamp, temperature, humidity, pressure, ext
            FROM mediciones
            WHERE node_id = ?
        ''', (node_id,))

        datos = cursor.fetchall()  # Obtener datos

        print(f"✅ Se obtuvieron {len(datos)} mediciones para el nodo {node_id}.")
        return datos  # Siempre retorna los 3 valores

    except sqlite3.Error as e:
        print(f"⚠️ Error al obtener datos del nodo {node_id}: {e}")
        return conn, cursor, []  # Retorna lista vacía en caso de error
# Inicializar la base de datos al ejecutar este script
if __name__ == "__main__":
    inicializar_db()
