import os
import json
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from database import obtener_mediciones_por_nodo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "graficas_resumen_email")
CONFIG_NODOS = os.path.join(BASE_DIR, "nodos_resumen.json")
NOMBRES_FILE = os.path.join(BASE_DIR, "sensor_nombres.json")

def cargar_nodos_resumen():
    if os.path.exists(CONFIG_NODOS):
        with open(CONFIG_NODOS, "r") as f:
            return json.load(f).get("nodos", [])
    return []

def cargar_nombres():
    if os.path.exists(NOMBRES_FILE):
        with open(NOMBRES_FILE, "r") as f:
            return json.load(f)
    return {}

def graficar_variable(df, variable, nombre_sensor, ruta_salida):
    if variable not in df.columns or df[variable].isna().all():
        return
    plt.figure(figsize=(8, 4))
    plt.plot(df["timestamp"], df[variable], marker="o", linewidth=1)
    plt.xlabel("Tiempo")
    plt.ylabel(variable.capitalize())
    plt.title(f"{variable.capitalize()} - {nombre_sensor}")
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(ruta_salida)
    plt.close()

def generar_resumen_graficas():
    print("📊 Generando nuevas gráficas resumen...")

    nodos = cargar_nodos_resumen()
    nombres = cargar_nombres()

    # Limpiar carpeta temporal
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    imagenes_generadas = []

    for node_id in nodos:
        datos = obtener_mediciones_por_nodo(node_id)
        if not datos:
            print(f"⚠️ Nodo {node_id} no tiene datos.")
            continue

        df = pd.DataFrame(datos, columns=["timestamp", "temperature", "humidity", "pressure", "ext"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        is_exterior = df["ext"].iloc[0] == 1
        tipo = "exterior" if is_exterior else "interior"

        nombre_sensor = nombres.get(str(node_id), f"Sensor {node_id}")
        nombre_carpeta = f"{nombre_sensor.replace(' ', '_')}_{tipo}_{node_id}"
        carpeta_nodo = os.path.join(TEMP_DIR, nombre_carpeta)
        os.makedirs(carpeta_nodo, exist_ok=True)

        # Siempre temperatura
        img_temp = os.path.join(carpeta_nodo, "temperatura.png")
        graficar_variable(df, "temperature", nombre_sensor, img_temp)
        if os.path.exists(img_temp):
            imagenes_generadas.append(img_temp)
            print(f"✅ Guardada: {img_temp}")

        if not is_exterior:
            # Solo interiores → humedad y presión
            img_hum = os.path.join(carpeta_nodo, "humedad.png")
            graficar_variable(df, "humidity", nombre_sensor, img_hum)
            if os.path.exists(img_hum):
                imagenes_generadas.append(img_hum)
                print(f"✅ Guardada: {img_hum}")

            img_pres = os.path.join(carpeta_nodo, "presion.png")
            graficar_variable(df, "pressure", nombre_sensor, img_pres)
            if os.path.exists(img_pres):
                imagenes_generadas.append(img_pres)
                print(f"✅ Guardada: {img_pres}")

    if not imagenes_generadas:
        print("⚠️ No se generaron gráficas.")
    return imagenes_generadas
