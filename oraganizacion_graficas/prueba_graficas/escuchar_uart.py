import os
import json
import serial
import time
import subprocess
from collections import deque
from datetime import datetime

# Configuración de UART
PUERTO_SIMULADOR = "COM11"  # Puerto de simulación en Windows (VSPE)
PUERTO_REAL = "/dev/serial0"  # UART real en Raspberry Pi
BAUDRATE = 9600
BUFFER_FILE = "buffer_uart.json"

# Tamaño máximo del lote antes de llamar al recolector
LOTE_MAXIMO = 5

# Determinar si estamos en simulación o en hardware real
SIM_FLAG = os.path.join(os.getcwd(), "sim_mode.flag")

def es_modo_simulado():
    return os.path.exists(SIM_FLAG)

# Selección de puerto según el modo
puerto_serie = PUERTO_SIMULADOR if es_modo_simulado() else PUERTO_REAL

# Cola en memoria para almacenar las mediciones temporalmente
mediciones_queue = deque()

def llamar_recolector_uart():
    """ Llama a recolector_uart.py para procesar datos """
    print(f"🚀 Llamando a recolector_uart.py con {len(mediciones_queue)} mediciones completas")

    while len(mediciones_queue) >= LOTE_MAXIMO:
        lote = [mediciones_queue.popleft() for _ in range(LOTE_MAXIMO)]

        # Guardar lote en buffer para que recolector lo procese
        with open(BUFFER_FILE, "w") as file:
            json.dump(lote, file, indent=4)

        # Llamar a recolector_uart.py para procesar este lote
        subprocess.run(["python", "recolector_uart.py"])

try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando en {puerto_serie} para recibir datos...")

        medicion_actual = []
        timestamp = None  # Timestamp de la medición

        while True:
            # Leer una línea de datos desde UART
            linea = uart.readline().decode("utf-8").strip()
            if not linea:
                continue

            # Si es la primera línea (MAC), capturamos el timestamp
            if "MAC: " in linea:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            # Guardar la línea con su timestamp
            medicion_actual.append(f"{timestamp}, {linea}")

            # Una medición completa son 5 líneas
            if len(medicion_actual) == 5:
                mediciones_queue.append(medicion_actual)
                print(f"✅ Nueva medición almacenada: {medicion_actual}")
                medicion_actual = []

            # Si hay muchas mediciones, hacer múltiples llamadas a recolector_uart.py
            if len(mediciones_queue) >= LOTE_MAXIMO:
                print(mediciones_queue)
                llamar_recolector_uart()

            time.sleep(0.1)

except serial.SerialException as e:
    print(f"❌ Error al abrir {puerto_serie}: {e}")

except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Guardando mediciones pendientes y cerrando...")
    llamar_recolector_uart()
    print("🔚 Escucha de UART detenida.")
