import os
import serial
import time
import json
from collections import deque

# Configuración de UART
PUERTO_SIMULADOR = "COM11"  # Puerto de simulación en Windows (VSPE)
PUERTO_REAL = "/dev/serial0"  # UART real en Raspberry Pi
BAUDRATE = 9600
BUFFER_FILE = "buffer_uart.json"  # Archivo donde se almacenarán temporalmente los datos
SIM_FLAG = os.path.join(os.getcwd(), "sim_mode.flag")  # Archivo que indica si estamos en simulación

# Determinar si estamos en simulación o en hardware real
def es_modo_simulado():
    return os.path.exists(SIM_FLAG)

# Determinar qué puerto usar (simulación vs UART real)
puerto_serie = PUERTO_SIMULADOR if es_modo_simulado() else PUERTO_REAL if os.path.exists(PUERTO_REAL) else "/dev/ttyS0"
modo = "SIMULADO" if es_modo_simulado() else "REAL"
print(f"🔹 Modo {modo} detectado. Usando puerto: {puerto_serie}")

# **Lista de arrays donde cada fila es una medición completa**
buffer_mediciones = deque()

# Cargar buffer desde archivo si existe
if os.path.exists(BUFFER_FILE):
    with open(BUFFER_FILE, "r") as file:
        try:
            buffer_mediciones.extend(json.load(file))
        except json.JSONDecodeError:
            buffer_mediciones.clear()  # Si hay un error en el JSON, reiniciamos el buffer

# Abrir UART y comenzar a leer datos
try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando en {puerto_serie} para recibir datos...")

        lectura_actual = []  # Buffer temporal para una medición completa

        while True:
            linea = uart.readline().decode("utf-8").strip()
            if not linea:
                continue

            # Agregar la línea a la fila actual
            lectura_actual.append(linea)

            # Si la lectura tiene 5 líneas completas, verificar si es nueva
            if len(lectura_actual) == 5:
                nueva_medicion = lectura_actual.copy()

                # Solo guardar si la medición es diferente a TODAS las que hay en el buffer
                if nueva_medicion not in buffer_mediciones:
                    buffer_mediciones.append(nueva_medicion)
                    print(f"✅ Nueva medición almacenada en buffer: {buffer_mediciones[-1]}")

                    # Guardar el buffer en un archivo para que `recolector_uart.py` lo lea
                    with open(BUFFER_FILE, "w") as file:
                        json.dump(list(buffer_mediciones), file, indent=4)

                lectura_actual.clear()  # Limpiar buffer temporal para la siguiente medición

            time.sleep(0.01)  # Pequeña espera para evitar saturación del puerto

except serial.SerialException as e:
    print(f"❌ Error al abrir {puerto_serie}: {e}")
except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Guardando el buffer en archivo...")

    # Guardar cualquier dato restante antes de salir
    with open(BUFFER_FILE, "w") as file:
        json.dump(list(buffer_mediciones), file, indent=4)

    print("🔚 Escucha de UART detenida.")
