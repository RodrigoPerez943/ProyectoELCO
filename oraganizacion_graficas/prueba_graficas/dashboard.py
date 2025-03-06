from flask import Flask, render_template, jsonify
import os
import pandas as pd
import plotly.express as px
import sqlite3
from database import obtener_mediciones_por_nodo

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mediciones.db")

def conectar_db():
    """Conectar a la base de datos y devolver la conexión."""
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/')
def index():
    """
    Página principal con lista de nodos disponibles.
    Se recarga automáticamente cada 5 segundos con un <script>.
    """
    nodos = set()
    
    conn = conectar_db()
    cursor = conn.cursor()

    # Obtener nodos distintos en la base de datos
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    for row in cursor.fetchall():
        nodos.add(f"nodo_{row[0]}")

    conn.close()

    if not nodos:
        return "⚠️ No hay nodos registrados en la base de datos.", 404

    # En 'index.html' colocarás un pequeño script para recargar cada 5s,
    # o bien puedes inyectar <meta http-equiv="refresh" content="5"> en el HTML.
    return render_template("index.html", nodos=sorted(nodos))

@app.route('/seleccionar_grafica/<nodo_id>')
def seleccionar_grafica(nodo_id):
    """Página para seleccionar qué gráfica ver."""
    return render_template("seleccionar_grafica.html", nodo_id=nodo_id)

@app.route('/graficas/<nodo_id>/temperature')
def ver_grafica_temperature(nodo_id):
    """Generar un gráfico dinámico de temperatura para el nodo y refrescarlo cada 5s."""
    try:
        node_id_int = int(nodo_id.split("_")[-1])  # Extraer ID numérico
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig = px.line(
            df,
            x="timestamp",
            y="temperature",
            title=f"Temperatura del Nodo {nodo_id}",
            labels={"timestamp": "Hora del día", "temperature": "Temperatura (°C)"},
            markers=True
        )
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        # Convertir la figura a HTML.
        html_grafica = fig.to_html(full_html=True)

        # Inyectar un meta-refresh de 5s para que se recargue sola la página.
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/humidity')
def ver_grafica_humidity(nodo_id):
    """Generar un gráfico dinámico de humedad para el nodo y refrescarlo cada 5s."""
    try:
        node_id_int = int(nodo_id.split("_")[-1])
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig = px.line(
            df,
            x="timestamp",
            y="humidity",
            title=f"Humedad medida por el Nodo {nodo_id}",
            labels={"timestamp": "Hora del día", "humidity": "Humedad (g/m^3)"},
            markers=True
        )
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        html_grafica = fig.to_html(full_html=True)
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/pressure')
def ver_grafica_pressure(nodo_id):
    """Generar un gráfico dinámico de presión para el nodo y refrescarlo cada 5s."""
    try:
        node_id_int = int(nodo_id.split("_")[-1])
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig = px.line(
            df,
            x="timestamp",
            y="pressure",
            title=f"Presión medida por el Nodo {nodo_id}",
            labels={"timestamp": "Hora del día", "pressure": "Presión (hPa)"},
            markers=True
        )
        fig.update_xaxes(dtick=60000, tickformat="%H:%M")

        html_grafica = fig.to_html(full_html=True)
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

# Hemos eliminado toda referencia a WebSocket y socketio.
# No definimos @socketio.on('connect') ni emitimos eventos.

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
