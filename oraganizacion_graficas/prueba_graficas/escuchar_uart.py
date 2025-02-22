import os
import json
import serial
import time
import subprocess

# Configuración de UART
PUERTO_SIMULADOR = "COM11"  # Puerto en Windows (VSPE)
PUERTO_REAL = "/dev/serial0"  # UART en Raspberry Pi
BAUDRATE = 9600
BUFFER_FILE = "buffer_uart.json"
SIM_FLAG = os.path.join(os.getcwd(), "sim_mode.flag")

# Determinar si estamos en simulación o en hardware real
def es_modo_simulado():
    return os.path.exists(SIM_FLAG)

# Determinar qué puerto usar
puerto_serie = PUERTO_SIMULADOR if es_modo_simulado() else PUERTO_REAL

# Lista temporal para almacenar una medición completa (5 lecturas)
medicion_actual = []

# Abrir UART y comenzar a leer datos
try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando en {puerto_serie} para recibir datos...")

        while True:
            # Leer una línea de datos desde UART
            linea = uart.readline().decode("utf-8").strip()
            if not linea:
                continue

            # Almacenar la lectura en la medición actual
            medicion_actual.append(linea)

            # Si ya tenemos 5 lecturas, guardamos la medición y procesamos
            if len(medicion_actual) == 5:
                # Leer el buffer actual si existe
                if os.path.exists(BUFFER_FILE):
                    try:
                        with open(BUFFER_FILE, "r") as file:
                            buffer_mediciones = json.load(file)
                    except json.JSONDecodeError:
                        buffer_mediciones = []
                else:
                    buffer_mediciones = []

                # Agregar la nueva medición al buffer sin eliminar nada
                buffer_mediciones.append(medicion_actual)

                # Guardar en JSON correctamente como lista
                with open(BUFFER_FILE, "w") as file:
                    json.dump(buffer_mediciones, file, indent=4)

                print(f"✅ Nueva medición almacenada en buffer: {medicion_actual}")

                # Llamar a recolector_uart pasando la medición completa
                subprocess.Popen(["python", "recolector_uart.py", json.dumps(medicion_actual)])

                # Reiniciar la lista para la siguiente medición
                medicion_actual = []

except serial.SerialException as e:
    print(f"❌ Error al abrir {puerto_serie}: {e}")
except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Guardando el buffer en archivo...")
