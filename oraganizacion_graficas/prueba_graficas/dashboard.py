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

@app.route('/seleccionar_grafica/<nodo_id>')
def seleccionar_grafica(nodo_id):
    """ Página para seleccionar qué gráfica ver """
    return render_template("seleccionar_grafica.html", nodo_id=nodo_id)


@app.route('/graficas/<nodo_id>/temperature')
def ver_grafica_temperature(nodo_id):
    """ Generar gráfico dinámico para el nodo """
    try:
        node_id_int = int(nodo_id.split("_")[-1])  # Extraer ID numérico
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        # Convertir a DataFrame
        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Crear gráfico de temperatura interactivo con Plotly
        fig = px.line(df, x="timestamp", y="temperature", title=f"Temperatura del Nodo {nodo_id}",
                      labels={"timestamp": "Hora del día", "temperature": "Temperatura (°C)"}, markers=True)
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        return fig.to_html(full_html=False)

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})
    

@app.route('/graficas/<nodo_id>/humidity')
def ver_grafica_humidity(nodo_id):
    """ Generar gráfico dinámico para el nodo """
    try:
        node_id_int = int(nodo_id.split("_")[-1])  # Extraer ID numérico
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        # Convertir a DataFrame
        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Crear gráfico de humedad interactivo con Plotly
        fig = px.line(df, x="timestamp", y="humidity", title=f"Humedad medida por el Nodo {nodo_id}",
                      labels={"timestamp": "Hora del día", "humidity": "Humedad (g/m^3)"}, markers=True)
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        return fig.to_html(full_html=False)

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})
    
@app.route('/graficas/<nodo_id>/pressure')
def ver_grafica_pressure(nodo_id):
    """ Generar gráfico dinámico para el nodo """
    try:
        node_id_int = int(nodo_id.split("_")[-1])  # Extraer ID numérico
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        # Convertir a DataFrame
        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Crear gráfico de presión interactivo con Plotly
        fig = px.line(df, x="timestamp", y="pressure", title=f"Presión medida por el Nodo {nodo_id}",
                      labels={"timestamp": "Hora del día", "pressre": "Presión (hPa))"}, markers=True)
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        return fig.to_html(full_html=False)

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

# 🔴 WebSocket: Notificar a los clientes cuando haya una nueva medición
@socketio.on('connect')
def handle_connect():
    print("✅ Cliente conectado a WebSocket")

#def notificar_nuevo_nodo(nodo_id):
#    "Emitir evento cuando se registra un nuevo nodo en la base de datos"
#    print(f"📡 Nuevo nodo detectado: nodo_{nodo_id}")
#    socketio.emit('nuevo_nodo', {"nodo_id": f"nodo_{nodo_id}"})

def notificar_nueva_medicion(nodo_id):
    """Emitir evento a los clientes cuando hay una nueva medición"""
    print(f"📡 Enviando actualización para nodo {nodo_id}")
    socketio.emit('nueva_medicion', {"nodo_id": nodo_id})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
