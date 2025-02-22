import os
import csv
import json

# Archivos
BUFFER_FILE = "buffer_uart.json"
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

# Inicializar mapeo de MAC
mac_mapping = cargar_mac_mapping()

# Crear archivo CSV con encabezado si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
    print(f"✅ Archivo CSV creado: {CSV_FILE}")

def procesar_mediciones():
    """ Procesa todas las mediciones en el buffer """
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
            timestamp, mac = medicion[0].split(", ")  # Extraer timestamp y MAC
            temperature = float(medicion[1].split(": ")[1].strip())
            humidity = float(medicion[2].split(": ")[1].strip())
            pressure = float(medicion[3].split(": ")[1].strip())
            ext = float(medicion[4].split(": ")[1].strip())

            # Asignar node_id basado en la MAC
            node_id = obtener_node_id(mac, mac_mapping)

            batch.append([timestamp, node_id, temperature, humidity, pressure, ext])

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
