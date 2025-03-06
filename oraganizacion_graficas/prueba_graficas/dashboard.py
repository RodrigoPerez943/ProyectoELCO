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
    Se recarga automáticamente cada 5 segundos (vía JavaScript en `index.html`).
    """
    nodos = set()
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    for row in cursor.fetchall():
        nodos.add(f"nodo_{row[0]}")
    conn.close()

    if not nodos:
        return "⚠️ No hay nodos registrados en la base de datos.", 404

    return render_template("index.html", nodos=sorted(nodos))

@app.route('/seleccionar_grafica/<nodo_id>')
def seleccionar_grafica(nodo_id):
    """Página para seleccionar qué gráfica ver."""
    return render_template("seleccionar_grafica.html", nodo_id=nodo_id)

@app.route('/graficas/<nodo_id>/temperature')
def ver_grafica_temperature(nodo_id):
    """Genera la gráfica de temperatura forzando un tamaño grande (1400x800 px)."""
    try:
        node_id_int = int(nodo_id.split("_")[-1])
        datos = obtener_mediciones_por_nodo(node_id_int)
        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Crear figura con Plotly
        fig = px.line(
            df,
            x="timestamp",
            y="temperature",
            title=f"Temperatura del Nodo {nodo_id}",
            labels={"timestamp": "Hora del día", "temperature": "Temperatura (°C)"},
            markers=True
        )

        # Forzar un tamaño grande en píxeles:
        fig.update_layout(
            autosize=False,
            width=1400,
            height=800,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Generar HTML
        html_grafica = fig.to_html(full_html=True)

        # Insertar meta refresh (5s) + link a CSS
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>\n<link rel='stylesheet' href='/static/style.css'>\n"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/humidity')
def ver_grafica_humidity(nodo_id):
    """Genera la gráfica de humedad forzando tamaño grande (1400x800 px)."""
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

        fig.update_layout(
            autosize=False,
            width=1400,
            height=800,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        html_grafica = fig.to_html(full_html=True)
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>\n<link rel='stylesheet' href='/static/style.css'>\n"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/pressure')
def ver_grafica_pressure(nodo_id):
    """Genera la gráfica de presión forzando tamaño grande (1400x800 px)."""
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

        fig.update_layout(
            autosize=False,
            width=1400,
            height=800,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        html_grafica = fig.to_html(full_html=True)
        html_grafica = html_grafica.replace(
            "<head>",
            "<head>\n<meta http-equiv='refresh' content='5'/>\n<link rel='stylesheet' href='/static/style.css'>\n"
        )
        return html_grafica

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
