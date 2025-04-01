from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import pandas as pd
import plotly.express as px
import sqlite3
import serial 
from database import obtener_mediciones_por_nodo
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mediciones.db")
INTERVALO_FILE = os.path.join(BASE_DIR, "intervalo_config.json")

UART_PORT = "COM9"  # ⚠ Ajustar según el sistema operativo
BAUDRATE = 115200

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
    cursor.execute("SELECT DISTINCT node_id, ext FROM mediciones")
    for row in cursor.fetchall():
        #nodos.add(f"nodo_{row[0]}")
        if (row[1] == 1):
            nodos.add(f"sensor_exterior_{row[0]}")
        else:
            nodos.add(f"sensor_{row[0]}")    
    conn.close()

    return render_template("index.html", nodos=sorted(nodos))

@app.route('/seleccionar_grafica/<nodo_id>')
def seleccionar_grafica(nodo_id):
    """Página para seleccionar qué gráfica ver."""
    return render_template("seleccionar_grafica.html", nodo_id=nodo_id)

@app.route('/graficas/<nodo_id>/temperature')
def ver_grafica_temperature(nodo_id):
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
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Generar HTML
        html_grafica = fig.to_html(full_html=True)

        # Insertar meta refresh (5s) + link a CSS
        # Envolver en un contenedor para control de tamaño
        html_final = f"""
        <html>
        <head>
            <meta http-equiv='refresh' content='5'/>
            <link rel='stylesheet' href='/static/style.css'>
        </head>
        <body>
            <div class="graph-container">
                {html_grafica}
            </div>
        </body>
        </html>
        """
        return html_final

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/humidity')
def ver_grafica_humidity(nodo_id):
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
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        html_grafica = fig.to_html(full_html=True)
        html_final = f"""
        <html>
        <head>
            <meta http-equiv='refresh' content='5'/>
            <link rel='stylesheet' href='/static/style.css'>
        </head>
        <body>
            <div class="graph-container">
                {html_grafica}
            </div>
        </body>
        </html>
        """
        return html_final

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route('/graficas/<nodo_id>/pressure')
def ver_grafica_pressure(nodo_id):
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
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        html_grafica = fig.to_html(full_html=True)
        html_final = f"""
        <html>
        <head>
            <meta http-equiv='refresh' content='5'/>
            <link rel='stylesheet' href='/static/style.css'>
        </head>
        <body>
            <div class="graph-container">
                {html_grafica}
            </div>
        </body>
        </html>
        """
        return html_final

    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

def enviar_intervalo_uart(intervalo):
    """Envia el intervalo de medición por UART a la Raspberry Pi."""
    try:
        with serial.Serial(UART_PORT, BAUDRATE, timeout=1) as ser:
            comando = f"INTERVALO:{intervalo}\n"
            ser.write(comando.encode())
            print(f"📡 Intervalo de medición enviado: {intervalo} segundos")
    except Exception as e:
        print(f"⚠️ Error al enviar datos por UART: {e}")

def guardar_intervalo(intervalo):
    """Guarda el intervalo en un archivo JSON."""
    with open(INTERVALO_FILE, "w") as file:
        json.dump({"intervalo": intervalo}, file)

def obtener_intervalo():
    """Obtiene el intervalo almacenado, o devuelve 60s por defecto."""
    if os.path.exists(INTERVALO_FILE):
        with open(INTERVALO_FILE, "r") as file:
            data = json.load(file)
            return data.get("intervalo", 60)
    return 60  # 📌 Valor por defecto

@app.route('/ajustes', methods=["GET", "POST"])
def ajustes():
    """Página de configuración del intervalo de medición."""
    intervalo_actual = obtener_intervalo()  # 📌 Obtener intervalo actual

    if request.method == "POST":
        horas = int(request.form.get("horas", 0))
        minutos = int(request.form.get("minutos", 0))
        segundos = int(request.form.get("segundos", 0))

        nuevo_intervalo = horas * 3600 + minutos * 60 + segundos  # Convertir a segundos

        if nuevo_intervalo > 0:
            guardar_intervalo(nuevo_intervalo)  # 📌 Guardar intervalo
            enviar_intervalo_uart(nuevo_intervalo)  # 📡 Enviar por UART
            print(f"✅ Intervalo actualizado: {nuevo_intervalo} segundos")
        return redirect(url_for("ajustes"))

    return render_template("ajustes.html", intervalo=intervalo_actual)  # 📌 Enviar intervalo actual a la web

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
