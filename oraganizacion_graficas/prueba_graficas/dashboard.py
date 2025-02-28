from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import os
import pandas as pd
import plotly.express as px
import sqlite3
from database import obtener_mediciones_por_nodo

app = Flask(__name__)
socketio = SocketIO(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mediciones.db")

def conectar_db():
    """ Conectar a la base de datos y devolver el cursor """
    conn = sqlite3.connect(DB_PATH)
    return conn  # ✅ Devolvemos solo la conexión

@app.route('/')
def index():
    """ Página principal con lista de nodos disponibles """
    nodos = set()
    
    conn = conectar_db()  # ✅ Solo obtenemos la conexión
    cursor = conn.cursor()

    # Obtener nodos distintos en la base de datos
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    for row in cursor.fetchall():
        nodos.add(f"nodo_{row[0]}")

    conn.close()

    if not nodos:
        return "⚠️ No hay nodos registrados en la base de datos.", 404

    return render_template("index.html", nodos=sorted(nodos))


@app.route('/graficas/<nodo_id>')
def ver_grafica(nodo_id):
    """ Generar gráfico dinámico para el nodo """
    try:
        node_id_int = int(nodo_id.split("_")[-1])  # Extraer ID numérico
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        # Convertir a DataFrame
        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Crear gráfico interactivo con Plotly
        fig = px.line(df, x="timestamp", y="temperature", title=f"Temperatura del Nodo {nodo_id}",
                      labels={"timestamp": "Hora del día", "temperature": "Temperatura (°C)"}, markers=True)
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        return fig.to_html(full_html=False)

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

# 🔴 WebSocket: Notificar a los clientes cuando haya una nueva medición
@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado a WebSocket")

def notificar_nueva_medicion(nodo_id):
    """Emitir evento a los clientes cuando hay una nueva medición"""
    print(f"📡 Enviando actualización para nodo {nodo_id}")
    socketio.emit('nueva_medicion', {"nodo_id": nodo_id})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
