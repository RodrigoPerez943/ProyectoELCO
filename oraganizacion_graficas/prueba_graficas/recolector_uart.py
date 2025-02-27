import os
import csv
import json
from database import insertar_medicion  # Importar función para guardar en la base de datos

# Obtener la ruta absoluta del directorio donde se ejecuta el script
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Definir rutas absolutas de los archivos en el mismo directorio del script
BUFFER_FILE = os.path.join(BASE_DIR, "buffer_uart.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
MAC_MAPPING_FILE = os.path.join(BASE_DIR, "mac_mapping.json")

# Cargar asignaciones de MAC si existen
def cargar_mac_mapping():
    if os.path.exists(MAC_MAPPING_FILE):
        with open(MAC_MAPPING_FILE, "r") as file:
            return json.load(file)
    return {}

# Guardar asignaciones de MAC
def guardar_mac_mapping(mac_mapping):
    with open(MAC_MAPPING_FILE, "w") as file:
        json.dump(mac_mapping, file, indent=4)

# Obtener o asignar un node_id a una MAC
def obtener_node_id(mac_address, mac_mapping):
    if mac_address in mac_mapping:
        return mac_mapping[mac_address]
    else:
        new_node_id = len(mac_mapping) + 1
        mac_mapping[mac_address] = new_node_id
        guardar_mac_mapping(mac_mapping)
        return new_node_id

# Inicializar mapeo de MAC
mac_mapping = cargar_mac_mapping()

# Crear archivo CSV con encabezado si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
    print(f"✅ Archivo CSV creado en: {CSV_FILE}")

def procesar_mediciones():
    """ Procesa todas las mediciones en el buffer y las guarda en CSV y la base de datos """
    if not os.path.exists(BUFFER_FILE):
        print("⚠️ No hay datos en el buffer para procesar.")
        return

    try:
        with open(BUFFER_FILE, "r") as file:
            mediciones = json.load(file)
    except json.JSONDecodeError:
        print("⚠️ Error al leer el buffer. Posible corrupción de datos.")
        return

    if not mediciones:
        return  # Nada que procesar

    batch = []
    for medicion in mediciones:
        try:
            # Extraer valores en el orden correcto
            timestamp, mac, temperature, humidity, pressure, ext = medicion

            # Convertir valores numéricos
            temperature = float(temperature)
            humidity = float(humidity)
            pressure = float(pressure)
            ext = float(ext)

            # Asignar node_id basado en la MAC
            node_id = obtener_node_id(mac, mac_mapping)

            # Guardar en lista para CSV
            batch.append([timestamp, node_id, temperature, humidity, pressure, ext])

            # Guardar en la base de datos
            insertar_medicion(timestamp, node_id, temperature, humidity, pressure)
            print(f"✅ Medición guardada en BD y CSV: Nodo {node_id} | {temperature}°C, {humidity}%, {pressure} hPa")

        except Exception as e:
            print(f"⚠️ Error al procesar una línea del buffer: {e}")

    # Guardar en formato CSV
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(batch)

    print(f"✅ {len(batch)} mediciones procesadas y guardadas en el CSV.")

    # Vaciar el buffer después de procesarlo
    with open(BUFFER_FILE, "w") as file:
        json.dump([], file)

if __name__ == "__main__":
    procesar_mediciones()
