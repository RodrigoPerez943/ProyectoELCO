import os
import csv
import json
import time
from datetime import datetime

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

# Guardar asignaciones de MAC sin bloquear el programa
def guardar_mac_mapping(mac_mapping):
    try:
        with open(MAC_MAPPING_FILE, "w") as file:
            json.dump(mac_mapping, file, indent=4)
    except Exception as e:
        print(f"⚠️ No se pudo guardar el mapeo MAC: {e}")

# Obtener o asignar un node_id a una MAC
def obtener_node_id(mac_address, mac_mapping):
    if mac_address in mac_mapping:
        return mac_mapping[mac_address]
    else:
        new_node_id = len(mac_mapping) + 1  # Generar un nuevo ID
        mac_mapping[mac_address] = new_node_id
        guardar_mac_mapping(mac_mapping)  # Guardar sin bloquear la lectura
        return new_node_id

# Inicializar mapeo de MAC
mac_mapping = cargar_mac_mapping()

# Crear archivo CSV con encabezado si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
    print(f"✅ Archivo CSV creado: {CSV_FILE}")

# Monitorear el buffer y procesar datos en tiempo real
print("🔍 Monitoreando buffer para capturar nuevas mediciones...")

while True:
    if os.path.exists(BUFFER_FILE):
        with open(BUFFER_FILE, "r") as file:
            try:
                buffer_mediciones = json.load(file)
            except json.JSONDecodeError:
                buffer_mediciones = []

        # Si hay datos en el buffer, procesarlos
        if buffer_mediciones:
            lectura = buffer_mediciones.pop(0)  # Sacar el primer elemento (FIFO)

            try:
                mac = lectura[0].split(": ")[1].strip()
                temperature = float(lectura[1].split(": ")[1].strip())
                humidity = float(lectura[2].split(": ")[1].strip())
                pressure = float(lectura[3].split(": ")[1].strip())
                ext = float(lectura[4].split(": ")[1].strip())

                # Generar timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Asignar node_id basado en la MAC
                node_id = obtener_node_id(mac, mac_mapping)

                # Guardar en formato de CSV
                with open(CSV_FILE, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, node_id, temperature, humidity, pressure, ext])

                print(f"✅ Medición guardada: {timestamp}, {node_id}, {temperature}, {humidity}, {pressure}, {ext}")

                # **Forzar la actualización del buffer JSON**
                with open(BUFFER_FILE, "w") as file:
                    json.dump(buffer_mediciones, file, indent=4)

                time.sleep(0.5)  # Pequeña pausa para evitar sobrecarga

            except Exception as e:
                print(f"⚠️ Error al procesar una línea del buffer: {e}")

    else:
        print("⚠️ No se encontró el archivo de buffer. Esperando...")
        time.sleep(1)  # Esperar si el archivo no existe
