import requests
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "ubicacion_config.json")

DEFAULT_UBICACION = {
    "nombre": "Madrid, España",
    "lat": "40.4168",
    "lon": "-3.7038"
}

API_KEY = "30c21fe4cce93dc74615fc10cce2dba0"  # 🔐 Reemplaza esto

def cargar_ubicacion():
    if not os.path.exists(CONFIG_PATH) or os.path.getsize(CONFIG_PATH) == 0:
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_UBICACION, f, indent=4)
        return DEFAULT_UBICACION

    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Archivo corrupto o vacío
        print("⚠️ Archivo de ubicación corrupto, usando valores por defecto.")
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_UBICACION, f, indent=4)
        return DEFAULT_UBICACION

def obtener_temperaturas_openweather():
    config = cargar_ubicacion()
    lat = config.get("lat")
    lon = config.get("lon")

    if API_KEY == "TU_API_KEY_AQUI":
        print("❌ API KEY no configurada.")
        return []

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()  # 🔒 Lanza error si la respuesta no es 200

        data = response.json()
        if "list" not in data:
            print(f"⚠️ Respuesta inesperada: {data}")
            return []

        temperaturas = []
        for entrada in data["list"]:
            timestamp = entrada["dt_txt"]
            temp = entrada["main"]["temp"]
            temperaturas.append((timestamp, temp))

        print(f"🌍 Datos meteorológicos cargados para: {config['nombre']}")
        return temperaturas

    except Exception as e:
        print(f"❌ Error al obtener datos de OpenWeatherMap: {e}")
        return []
