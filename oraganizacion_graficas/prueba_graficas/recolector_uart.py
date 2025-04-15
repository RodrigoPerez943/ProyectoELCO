import os
import csv
import json
from database import insertar_medicion, conectar_db, crear_tabla
from alertas import verificar_alertas
from alertas import enviar_alerta_email


# Crear la tabla si no existe
crear_tabla()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

BUFFER_FILE = os.path.join(BASE_DIR, "buffer_uart.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
MAC_MAPPING_FILE = os.path.join(BASE_DIR, "mac_mapping.json")

def cargar_mac_mapping():
    if os.path.exists(MAC_MAPPING_FILE):
        with open(MAC_MAPPING_FILE, "r") as file:
            return json.load(file)
    return {}

def guardar_mac_mapping(mac_mapping):
    with open(MAC_MAPPING_FILE, "w") as file:
        json.dump(mac_mapping, file, indent=4)

def obtener_node_id(mac_address, mac_mapping):
    if mac_address in mac_mapping:
        return mac_mapping[mac_address]
    else:
        new_node_id = len(mac_mapping) + 1
        mac_mapping[mac_address] = new_node_id
        guardar_mac_mapping(mac_mapping)

        # Generar posición por defecto
        pos_file = os.path.join(BASE_DIR, "sensor_positions.json")
        if os.path.exists(pos_file):
            with open(pos_file, "r") as f:
                posiciones = json.load(f)
        else:
            posiciones = {}

        if str(new_node_id) not in posiciones:
            x = 5 + (new_node_id - 1) * 10 % 90
            y = 5 + ((new_node_id - 1) * 10 // 90) * 10
            posiciones[str(new_node_id)] = {"x": x, "y": y}
            with open(pos_file, "w") as f:
                json.dump(posiciones, f, indent=4)

        return new_node_id

mac_mapping = cargar_mac_mapping()

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
    print(f"✅ Archivo CSV creado en: {CSV_FILE}")

def procesar_mediciones():
    """ Procesa las mediciones en el buffer y las guarda en CSV y la base de datos. """
    if not os.path.exists(BUFFER_FILE) or os.path.getsize(BUFFER_FILE) == 0:
        print("⚠️ No hay datos en el buffer para procesar.")
        return

    try:
        with open(BUFFER_FILE, "r") as file:
            mediciones = json.load(file)
    except json.JSONDecodeError:
        print("⚠️ Error al leer el buffer. Posible corrupción de datos.")
        return

    if not mediciones:
        print("⚠️ Buffer vacío, no hay datos para procesar.")
        return

    batch = []

    for medicion in mediciones:
        try:
            timestamp, mac, temperature, humidity, pressure, ext = medicion

            temperature = float(temperature)
            humidity = float(humidity)
            pressure = float(pressure)
            ext = float(ext)

            node_id = obtener_node_id(mac, mac_mapping)

            batch.append([timestamp, node_id, temperature, humidity, pressure, ext])

            # Insertar en la base de datos
            insertar_medicion(timestamp, node_id, temperature, humidity, pressure, ext)

            # 🚨 Verificar alertas tras insertar la medición
            verificar_alertas(node_id, temperature)

        except Exception as e:
            mensaje = f"⚠️ Error al procesar una línea del buffer: {e}"
            if 'node_id' in locals():
                mensaje += f" (Nodo {node_id})"
            print(mensaje)

    if batch:
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(batch)         

        print(f"✅ {len(batch)} mediciones procesadas y guardadas en el CSV.")

    with open(BUFFER_FILE, "w") as file:
        json.dump([], file)

if __name__ == "__main__":
    procesar_mediciones()
