import os
import csv
import json
import sys
from datetime import datetime

# Archivos
CSV_FILE = "sensor_data.csv"
MAC_MAPPING_FILE = "mac_mapping.json"

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

# Verificar que se pasó una medición como argumento
if len(sys.argv) < 2:
    print("⚠️ No se recibió ninguna medición como argumento.")
    sys.exit(1)

# Convertir el argumento JSON en lista
try:
    medicion = json.loads(sys.argv[1])
except json.JSONDecodeError:
    print("⚠️ Error al decodificar la medición recibida.")
    sys.exit(1)

try:
    # Extraer los datos de la medición
    mac = medicion[0].split(": ")[1].strip()
    temperature = float(medicion[1].split(": ")[1].strip())
    humidity = float(medicion[2].split(": ")[1].strip())
    pressure = float(medicion[3].split(": ")[1].strip())
    ext = float(medicion[4].split(": ")[1].strip())

    # Generar timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Inicializar mapeo de MAC y asignar node_id
    mac_mapping = cargar_mac_mapping()
    node_id = obtener_node_id(mac, mac_mapping)
    file_exists = os.path.exists(CSV_FILE)
    # Guardar en CSV
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])

        writer.writerow([timestamp, node_id, temperature, humidity, pressure, ext])

    print(f"✅ Medición guardada: {timestamp}, {node_id}, {temperature}, {humidity}, {pressure}, {ext}")

except Exception as e:
    print(f"⚠️ Error al procesar la medición: {e}")
