import serial
import csv
import os
import time
import sys

# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo de bandera que indica si estamos en simulación
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")

# Determinar el puerto UART según el modo
if os.path.exists(SIM_FLAG):
    print("🔧 Modo de simulación detectado. Usando UART virtual en COM11.")
    UART_PORT = "COM11"  # Puerto virtual creado por `setup_puertos_virtuales.py`
else:
    print("📡 Modo real detectado. Usando UART físico en /dev/serial0 o COM1.")
    UART_PORT = "/dev/serial0" if os.name != "nt" else "COM1"

BAUDRATE = 9600
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")

# Iniciar conexión serie
try:
    ser = serial.Serial(UART_PORT, BAUDRATE, timeout=None)
except serial.SerialException as e:
    print(f"❌ Error al abrir el puerto {UART_PORT}: {e}")
    sys.exit(1)

# Crear el archivo CSV si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w") as file:
        file.write("temperature,humidity,timestamp,node_id,pressure\n")

print(f"📡 Esperando datos UART en {UART_PORT}...")

while True:
    try:
        linea = ser.readline().decode("utf-8").strip()

        if linea:
            datos = linea.split(",")
            if len(datos) == 5:
                with open(CSV_FILE, "a") as file:
                    file.write(",".join(datos) + "\n")
                print(f"✅ Medida guardada en CSV: {linea}")
    except Exception as e:
        print(f"⚠️ Error en UART: {e}")
