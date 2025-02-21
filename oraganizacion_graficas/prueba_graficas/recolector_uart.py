import os
import csv
import json
import serial
import time
from datetime import datetime
import serial.tools.list_ports

# Configuración de UART
PUERTO_SIMULADOR = "COM11"  # Puerto de simulación en Windows (VSPE)
PUERTO_REAL = "/dev/serial0"  # UART real en Raspberry Pi
BAUDRATE = 9600
CSV_FILE = "sensor_data.csv"
MAC_MAPPING_FILE = "mac_mapping.json"
SIM_FLAG = os.path.join(os.getcwd(), "sim_mode.flag")  # Archivo que indica si estamos en simulación

# Determinar si estamos en simulación o en hardware real
def es_modo_simulado():
    return os.path.exists(SIM_FLAG)  # Si el archivo existe, estamos en modo simulado

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
        new_node_id = len(mac_mapping) + 1  # Generar un nuevo ID
        mac_mapping[mac_address] = new_node_id
        guardar_mac_mapping(mac_mapping)
        return new_node_id

# Inicializar mapeo de MAC
mac_mapping = cargar_mac_mapping()

# Determinar qué puerto usar (simulación vs UART real)
if es_modo_simulado():
    puerto_serie = PUERTO_SIMULADOR
    print("🟡 Modo SIMULADO detectado. Usando puerto virtual:", PUERTO_SIMULADOR)
else:
    # En una Raspberry Pi, usar el puerto real `/dev/serial0` o `/dev/ttyS0`
    puerto_serie = PUERTO_REAL if os.path.exists(PUERTO_REAL) else "/dev/ttyS0"
    print("🟢 Modo REAL detectado. Usando puerto UART:", puerto_serie)

# Abrir UART y comenzar a leer datos
try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando en {puerto_serie} para recibir datos...")
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w") as file:
                file.write("temperature,humidity,timestamp,node_id,pressure\n")

        while True:
            # Leer una línea de datos desde UART
            linea = uart.readline().decode("utf-8").strip()
            if not linea:
                continue

            # Dividir los datos esperados: "MAC,TEMPERATURA,HUMEDAD,TIMESTAMP,PRESION"
            try:
                temperature, humidity, mac_address, pressure = linea.split(",")
                #timestamp = datetime.now().timestamp()
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(timestamp)
                node_id = obtener_node_id(mac_address, mac_mapping)  # Asignar node_id según MAC

                # Escribir en CSV
                with open(CSV_FILE, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([temperature, humidity, timestamp, node_id, pressure])

                print(f"✅ Datos guardados: node_id={node_id}, temp={temperature}, hum={humidity}, pres={pressure}, time={timestamp}")

            except ValueError:
                print(f"⚠️ Formato incorrecto recibido: {linea}")

            time.sleep(1)  # Pequeña espera para evitar saturación del puerto

except serial.SerialException as e:
    print(f"❌ Error al abrir {puerto_serie}: {e}")
except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Cerrando el recolector...")
