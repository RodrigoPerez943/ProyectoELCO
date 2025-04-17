from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import pandas as pd
import plotly.express as px
import sqlite3
import serial 
from database import obtener_mediciones_por_nodo
import json
import threading
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from alertas import ejecutar_resumen_periodico 
from datetime import datetime, timedelta
from openweather import obtener_temperaturas_openweather

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
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT node_id, temperature, humidity, pressure, ext, MAX(timestamp)
        FROM mediciones
        GROUP BY node_id
    ''')
    rows = cursor.fetchall()

    # Cargar nombres personalizados
    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    ids = {str(row[0]) for row in rows}
    for node_id in ids:
        if node_id not in nombres:
            nombres[node_id] = f"Sensor {node_id}"

    with open(nombres_file, "w") as f:
        json.dump(nombres, f, indent=4)

    tarjetas = []
    ahora = datetime.now()
    ultima_medicion = {}

    for row in rows:
        node_id = str(row[0])
        temperatura = row[1]
        humedad = row[2]
        presion = row[3]
        ext = row[4]
        timestamp = pd.to_datetime(row[5])
        tipo = "exterior" if ext == 1 else "interior"

        tarjetas.append({
            "id": node_id,
            "nombre": nombres.get(node_id, f"Sensor {node_id}"),
            "temperature": round(temperatura, 1) if temperatura is not None else "N/A",
            "humidity": round(humedad, 1) if humedad is not None else "N/A",
            "pressure": round(presion, 1) if presion is not None else "N/A",
            "tipo": tipo
        })

        ultima_medicion[node_id] = (ahora - timestamp).total_seconds()

    # Calcular estadísticas
    exteriores = [x for x in tarjetas if x["tipo"] == "exterior"]
    interiores = [x for x in tarjetas if x["tipo"] == "interior"]
    sensor_mas_caliente = max(tarjetas, key=lambda x: x["temperature"] if isinstance(x["temperature"], float) else -999)
    sensor_mas_humedo = max(interiores, key=lambda x: x["humidity"] if isinstance(x["humidity"], float) else -999)
    presiones = [x["pressure"] for x in interiores if isinstance(x["pressure"], float)]
    media_presion = round(sum(presiones) / len(presiones), 1) if presiones else "N/A"

    # Cargar alertas y contar las recientes
    alertas_file = os.path.join(BASE_DIR, "alertas_config.json")
    alertas_recientes = 0
    if os.path.exists(alertas_file):
        with open(alertas_file, "r") as f:
            alertas_data = json.load(f)
        hace_una_semana = ahora - timedelta(days=7)
        for config in alertas_data.values():
            estado = config.get("estado", {})
            for tipo, valor in estado.items():
                if valor == "alerta":
                    alertas_recientes += 1

    return render_template("index.html",
                           tarjetas=tarjetas,
                           nombres=nombres,
                           sensor_mas_caliente=sensor_mas_caliente,
                           sensor_mas_humedo=sensor_mas_humedo,
                           media_presion=media_presion,
                           alertas_semana=alertas_recientes,
                           ultima_medicion=ultima_medicion)



@app.route('/seleccionar_grafica/<nodo_id>')
def seleccionar_grafica(nodo_id):
    """Página para seleccionar qué gráfica ver."""

    node_id_int = int(nodo_id.split("_")[-1])
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ext FROM mediciones WHERE node_id=?", (node_id_int,))
    resultado = cursor.fetchone()
    es_exterior = resultado[0] == 1 if resultado else False
    

    # AÑADIR LOS NOMBRES DEL SENSOR JSON
    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    nombre_sensor = nombres.get(str(node_id_int), f"Sensor {node_id_int}")
    return render_template("seleccionar_grafica.html", nodo_id=nodo_id, es_exterior=es_exterior,nombre=nombre_sensor)


@app.route('/graficas/<nodo_id>/temperature')
def ver_grafica_temperature(nodo_id):
    try:
        node_id_int = int(nodo_id.split("_")[-1])
        datos = obtener_mediciones_por_nodo(node_id_int)
        if not datos:
            return jsonify({"error": f"No hay datos disponibles para el nodo {nodo_id}"})

        # Construir DataFrame de sensor
        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        is_exterior = int(df["ext"].mode()[0]) == 1

        # Cargar nombre del sensor
        nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
        if os.path.exists(nombres_file):
            with open(nombres_file, "r") as f:
                nombres = json.load(f)
        else:
            nombres = {}
        nombre = nombres.get(str(node_id_int), f"Sensor {node_id_int}")

        # Si es exterior, preparar datos de OpenWeather para enviarlos como trace estático al frontend
        openweather_trace = None
        if is_exterior:
            from openweather import obtener_temperaturas_openweather
            datos_open = obtener_temperaturas_openweather()
            print("✅ OpenWeatherMap cargado:")
            for t, temp in datos_open[:5]:
                print(f"{t} → {temp}")

            if datos_open:
                df_open = pd.DataFrame(datos_open, columns=["timestamp", "temperature"])
                df_open["timestamp"] = pd.to_datetime(df_open["timestamp"])

                openweather_trace = {
                    "x": df_open["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                    "y": df_open["temperature"].tolist(),
                    "mode": "lines+markers",
                    "name": "OpenWeatherMap",
                    "line": {"dash": "dot", "color": "orange"},
                    "marker": {"size": 9, "symbol": "circle"}
                }
            else:
                print("⚠️ No se encontraron datos de OpenWeatherMap")

        # Generar HTML base del gráfico con Plotly
        html_grafica = """
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <div id="graph"></div>
        """  # Solo dejamos el contenedor, el gráfico se construye por JS

        return render_template(
            "grafica.html",
            grafica=html_grafica,
            titulo=f"Temperatura de {nombre}",
            nodo_id=nodo_id,
            variable="temperature",
            openweather_trace=openweather_trace
        )

    except Exception as e:
        print("❌ Error en ver_grafica_temperature:", e)
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

        nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
        if os.path.exists(nombres_file):
            with open(nombres_file, "r") as f:
                nombres = json.load(f)
        else:
            nombres = {}

        nombre = nombres.get(str(node_id_int), f"Sensor {node_id_int}")

        fig = px.line(
            df,
            x="timestamp",
            y="pressure",
            labels={"timestamp": "Hora del día", "pressure": "Presión (hPa)"},
            markers=True
        )

        fig.update_layout(
            title=f"Presión medida por {nombre}",
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig.update_traces(name=f"Presión - {nombre}")

        html_grafica = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})

        return render_template(
            "grafica.html",
            grafica=html_grafica,
            titulo=f"Presión medida por {nombre}",
            nodo_id=nodo_id,
            variable="pressure",
            openweather_trace=None  # 👈 ¡esto es clave!
        )


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

        # Cargar nombre personalizado
        nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
        if os.path.exists(nombres_file):
            with open(nombres_file, "r") as f:
                nombres = json.load(f)
        else:
            nombres = {}

        nombre = nombres.get(str(node_id_int), f"Sensor {node_id_int}")

        fig = px.line(
            df,
            x="timestamp",
            y="humidity",
            labels={"timestamp": "Hora del día", "humidity": "Humedad (%)"},
            markers=True
        )

        fig.update_layout(
            title=f"Humedad medida por {nombre}",
            autosize=True,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig.update_traces(name=f"Humedad - {nombre}")

        html_grafica = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})

        return render_template(
            "grafica.html",
            grafica=html_grafica,
            titulo=f"Humedad medida por {nombre}",
            nodo_id=nodo_id,
            variable="humidity",
            openweather_trace=None
        )


    except Exception as e:
        return jsonify({"error": f"Error generando gráfica: {e}"})

@app.route("/api/datos_grafica/<nodo_id>/<variable>")
def api_datos_grafica(nodo_id, variable):
    try:
        node_id_int = int(nodo_id.split("_")[-1])
        datos = obtener_mediciones_por_nodo(node_id_int)

        if not datos:
            return jsonify({"timestamps": [], "valores": []})

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return jsonify({
            "timestamps": df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            "valores": df[variable].tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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

EMAIL_CONFIG_FILE = os.path.join(BASE_DIR, "email_config.json")

@app.route('/ajustes', methods=["GET", "POST"])
def ajustes():
    intervalo_actual = obtener_intervalo()

    # Leer configuración de correo
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as f:
            email_config = json.load(f)
    else:
        email_config = {}

    # Leer nodos
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    nodos = sorted(set(str(row[0]) for row in cursor.fetchall()))
    conn.close()

    # Leer nombres
    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            todos_los_nombres = json.load(f)
    else:
        todos_los_nombres = {}

    for node_id in nodos:
        if node_id not in todos_los_nombres:
            todos_los_nombres[node_id] = f"Sensor {node_id}"

    # Leer nodos incluidos en resumen
    nodos_resumen_file = os.path.join(BASE_DIR, "nodos_resumen.json")
    if os.path.exists(nodos_resumen_file):
        with open(nodos_resumen_file, "r") as f:
            nodos_resumen = json.load(f).get("nodos", [])
    else:
        nodos_resumen = []

    # Leer configuración de ubicación
    ubicacion_config_file = os.path.join(BASE_DIR, "ubicacion_config.json")
    if os.path.exists(ubicacion_config_file):
        with open(ubicacion_config_file, "r") as f:
            ubicacion_config = json.load(f)
    else:
        ubicacion_config = {
            "nombre": "Madrid, España",
            "lat": "40.4168",
            "lon": "-3.7038"
        }
        with open(ubicacion_config_file, "w") as f:
            json.dump(ubicacion_config, f, indent=4)

    # Procesar POST
    if request.method == "POST":
        # Guardar intervalo
        if "guardar_email" not in request.form:
            horas = int(request.form.get("horas", 0))
            minutos = int(request.form.get("minutos", 0))
            segundos = int(request.form.get("segundos", 0))
            nuevo_intervalo = horas * 3600 + minutos * 60 + segundos
            if nuevo_intervalo > 0:
                guardar_intervalo(nuevo_intervalo)
                enviar_intervalo_uart(nuevo_intervalo)

        # Guardar configuración de correo
        if "guardar_email" in request.form:
            nueva_config = {
                "sender": request.form.get("sender", ""),
                "password": request.form.get("password", ""),
                "recipient": request.form.get("recipient", ""),
                "smtp_server": request.form.get("smtp_server", ""),
                "smtp_port": int(request.form.get("smtp_port", 587))
            }
            with open(EMAIL_CONFIG_FILE, "w") as f:
                json.dump(nueva_config, f, indent=4)

        # Guardar selección de nodos para resumen
        if "guardar_nodos_resumen" in request.form:
            seleccionados = request.form.getlist("nodos_resumen")
            seleccionados_int = [int(s) for s in seleccionados]
            with open(nodos_resumen_file, "w") as f:
                json.dump({"nodos": seleccionados_int}, f, indent=4)

        # Guardar ubicación si se ha enviado
        if request.form.get("latitud") and request.form.get("longitud"):
            ubicacion_config = {
                "nombre": request.form.get("ubicacion_nombre", "Ciudad personalizada"),
                "lat": request.form.get("latitud"),
                "lon": request.form.get("longitud")
            }
            with open(ubicacion_config_file, "w") as f:
                json.dump(ubicacion_config, f, indent=4)

        return redirect(url_for("ajustes"))

    return render_template("ajustes.html",
                            intervalo=intervalo_actual,
                            email_config=email_config,
                            todos_los_nombres=todos_los_nombres,
                            nodos_resumen=[str(n) for n in nodos_resumen],
                            ubicacion_actual=ubicacion_config)  # 🔁 Pasamos todo

@app.route("/api/resumen_toggle", methods=["POST"])
def resumen_toggle():
    estado = request.json.get("resumen_activo", False)

    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as f:
            config = json.load(f)
    else:
        config = {}

    config["resumen_activo"] = estado

    with open(EMAIL_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    return jsonify({"ok": True, "resumen_activo": estado})

@app.route('/mapa_sensores', methods=["GET", "POST"])
def mapa_sensores():
    UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if request.method == "POST":
        imagen = request.files.get("imagen")
        if imagen:
            imagen.save(os.path.join(UPLOAD_FOLDER, "plano.png"))
            return redirect(url_for("mapa_sensores"))

    # Cargar última imagen si existe
    imagen_url = None
    ruta_imagen = os.path.join(UPLOAD_FOLDER, "plano.png")
    if os.path.exists(ruta_imagen):
        imagen_url = "/static/uploads/plano.png"

    # Cargar últimas temperaturas por nodo
    nodos = []
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT node_id, temperature FROM (
            SELECT node_id, temperature, MAX(timestamp) AS latest
            FROM mediciones
            GROUP BY node_id
        )
    ''')
    for row in cursor.fetchall():
        nodos.append({"id": row[0], "temp": row[1]})
    conn.close()

    # Convertir a string los IDs
    nodos_ids = [str(n["id"]) for n in nodos]

    # ------------------------
    # ✅ GENERAR NOMBRES SI FALTAN
    # ------------------------

    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    for node_id in nodos_ids:
        if node_id not in nombres:
            nombres[node_id] = f"Sensor {node_id}"

    with open(nombres_file, "w") as f:
        json.dump(nombres, f, indent=4)


    # ------------------------
    # ✅ GENERAR POSICIONES SI FALTAN
    # ------------------------

    pos_file = os.path.join(BASE_DIR, "sensor_positions.json")
    nodos_ids = [str(n["id"]) for n in nodos]

    if os.path.exists(pos_file):
        with open(pos_file, "r") as f:
            posiciones = json.load(f)
    else:
        posiciones = {}

    espaciado = 10
    x, y = 5, 5
    for node_id in nodos_ids:
        if node_id not in posiciones:
            posiciones[node_id] = {"x": x, "y": y}
            x += espaciado
            if x > 90:
                x = 5
                y += espaciado

    with open(pos_file, "w") as f:
        json.dump(posiciones, f, indent=4)

    return render_template(
    "mapa_sensores.html",
    imagen_url=imagen_url,
    nodos=nodos,
    posiciones=posiciones,
    nombres=nombres)
    



@app.route('/guardar_posiciones', methods=["POST"])
def guardar_posiciones():
    posiciones = request.get_json()
    pos_file = os.path.join(BASE_DIR, "sensor_positions.json")
    with open(pos_file, "w") as f:
        json.dump(posiciones, f, indent=4)
    return "✅ Posiciones guardadas correctamente."


@app.route('/api/temperaturas')
def api_temperaturas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT node_id, temperature
        FROM (
            SELECT node_id, temperature, MAX(timestamp) AS latest
            FROM mediciones
            GROUP BY node_id
        )
    ''')
    data = {str(row[0]): row[1] for row in cursor.fetchall()}
    conn.close()
    return jsonify(data)


@app.route('/nombres_sensores', methods=["GET", "POST"])
def nombres_sensores():
    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")

    # 🔹 Cargar nombres existentes
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    # 🔹 Leer node_id y ext (0: interior, 1: exterior)
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id, ext FROM mediciones")
    nodos_db = cursor.fetchall()
    conn.close()

    # 🔹 Generar estructura: { id: {"nombre": ..., "ext": ...} }
    nodos = {}
    for node_id, ext in nodos_db:
        node_id = str(node_id)
        nodos[node_id] = {
            "nombre": nombres.get(node_id, f"Sensor {node_id}"),
            "ext": bool(ext)
        }

    # 🔹 Si se ha enviado el formulario, actualizar nombres
    if request.method == "POST":
        nuevos_nombres = request.form.to_dict()
        solo_nombres = {k: v for k, v in nuevos_nombres.items()}
        with open(nombres_file, "w") as f:
            json.dump(solo_nombres, f, indent=4)
        return redirect(url_for("nombres_sensores"))

    return render_template("nombres_sensores.html", nodos=nodos)

@app.route("/alertas", methods=["GET", "POST"])
def alertas_config():
    alertas_file = os.path.join(BASE_DIR, "alertas_config.json")
    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")

    # 🔹 Cargar nombres personalizados
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    # 🔹 Cargar alertas existentes
    if os.path.exists(alertas_file):
        with open(alertas_file, "r") as f:
            alertas = json.load(f)
    else:
        alertas = {}

    # 🔹 Obtener nodos existentes de la base de datos
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    ids_db = sorted(set(str(row[0]) for row in cursor.fetchall()))

    # 🔹 Obtener si el nodo es exterior
    ext = {}
    for node_id in ids_db:
        cursor.execute("SELECT ext FROM mediciones WHERE node_id=? ORDER BY timestamp DESC LIMIT 1", (int(node_id),))
        fila = cursor.fetchone()
        ext[node_id] = fila[0] == 1 if fila else False
    conn.close()

    # 🔹 Generar estructura de nombres si falta alguno
    for node_id in ids_db:
        if node_id not in nombres:
            nombres[node_id] = f"Sensor {node_id}"

    if request.method == "POST":
        nuevas = {}
        for node_id in ids_db:
            if ext.get(node_id):  # Sensor exterior → solo temperatura
                nuevas[node_id] = {
                    "min_temp": request.form.get(f"min_temp_{node_id}", type=float),
                    "max_temp": request.form.get(f"max_temp_{node_id}", type=float)
                }
            else:  # Sensor interior → todos los límites
                nuevas[node_id] = {
                    "min_temp": request.form.get(f"min_temp_{node_id}", type=float),
                    "max_temp": request.form.get(f"max_temp_{node_id}", type=float),
                    "min_hum": request.form.get(f"min_hum_{node_id}", type=float),
                    "max_hum": request.form.get(f"max_hum_{node_id}", type=float),
                    "min_pres": request.form.get(f"min_pres_{node_id}", type=float),
                    "max_pres": request.form.get(f"max_pres_{node_id}", type=float),
                }

        with open(alertas_file, "w") as f:
            json.dump(nuevas, f, indent=4)
        return redirect(url_for("alertas_config"))

    return render_template("alertas.html", alertas=alertas, nombres=nombres, ext=ext)

@app.route("/comparar", methods=["GET", "POST"])
def comparar_sensores():
    variable = request.form.get("variable", "temperature") if request.method == "POST" else "temperature"

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id, ext FROM mediciones")
    raw_sensores = cursor.fetchall()

    # Mostrar todos para temperatura, solo interiores para humedad/presión
    if variable == "temperature":
        sensores = sorted(set(str(row[0]) for row in raw_sensores))
    else:
        sensores = sorted(set(str(row[0]) for row in raw_sensores if row[1] == 0))  # solo interiores

    conn.close()

    nombres_file = os.path.join(BASE_DIR, "sensor_nombres.json")
    nombres = {}
    if os.path.exists(nombres_file):
        with open(nombres_file, "r") as f:
            nombres = json.load(f)

    if request.method == "POST":
        
        seleccionados_raw = request.form.getlist("sensores")

        # Filtrar de nuevo en backend: solo válidos para la variable actual
        if variable == "temperature":
            seleccionados = seleccionados_raw
        else:
            # Solo interiores (ya filtrados en sensores)
            seleccionados = [s for s in seleccionados_raw if s in sensores]

        datos_graficas = []

        for node_id in seleccionados:
            node_id_int = int(node_id)
            datos = obtener_mediciones_por_nodo(node_id_int)
            if datos:
                df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                trace = {
                    "x": df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist(),
                    "y": df[variable].tolist(),
                    "mode": "lines+markers",
                    "name": nombres.get(node_id, f"Sensor {node_id}")
                }
                datos_graficas.append(trace)

        layout = {
            "title": f"Comparación de sensores - {variable.capitalize()}",
            "xaxis": {"title": "Hora"},
            "yaxis": {"title": variable.capitalize()},
            "margin": dict(l=40, r=20, t=50, b=40)
        }

        return render_template("comparar.html",
                               sensores=sensores,
                               nombres=nombres,
                               seleccionados=seleccionados,
                               variable=variable,
                               datos_graficas=datos_graficas,
                               layout=layout)

    # GET (primera carga)
    return render_template("comparar.html",
                           sensores=sensores,
                           nombres=nombres,
                           seleccionados=[],
                           variable="temperature",
                           datos_graficas=[],
                           layout={})


if __name__ == "__main__":
    # Lanzar resumen en segundo plano
    resumen_thread = threading.Thread(target=ejecutar_resumen_periodico, daemon=True)
    resumen_thread.start()

    # Ejecutar servidor web Flask
    app.run(host="0.0.0.0", port=5000, debug=True)


