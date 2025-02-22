import os
import json
import serial
import time
import subprocess
import threading

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

# Cola de mediciones y configuración de lotes
cola_mediciones = []
BATCH_SIZE = 5  # Número de mediciones antes de procesar
TIME_LIMIT = 2  # Tiempo máximo antes de procesar un lote (segundos)
last_process_time = time.time()

def procesar_lote():
    """ Procesa el lote de mediciones cuando se llena o cuando pasa el tiempo límite. """
    global cola_mediciones, last_process_time

    while True:
        time.sleep(1)  # Pequeña espera para evitar saturación

        # Verificar si hay suficiente data o si pasó el tiempo límite
        if len(cola_mediciones) >= BATCH_SIZE or (time.time() - last_process_time >= TIME_LIMIT and cola_mediciones):
            lote = cola_mediciones.copy()
            cola_mediciones.clear()
            last_process_time = time.time()

            # Enviar el lote a recolector_uart.py
            print(f"📤 Enviando lote de {len(lote)} mediciones a recolector_uart...")
            subprocess.Popen(["python", "recolector_uart.py", json.dumps(lote)])

# Iniciar el hilo de procesamiento de mediciones
threading.Thread(target=procesar_lote, daemon=True).start()

# Abrir UART y comenzar a leer datos
try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando en {puerto_serie} para recibir datos...")
        medicion_actual = []

        while True:
            # Leer una línea de datos desde UART
            linea = uart.readline().decode("utf-8").strip()
            if not linea:
                continue

            medicion_actual.append(linea)

            # Si ya tenemos 5 lecturas, agregamos la medición completa al lote
            if len(medicion_actual) == 5:
                cola_mediciones.append(medicion_actual.copy())  # Agregar a la cola
                medicion_actual = []  # Reiniciar la medición actual
                print(f"✅ Medición agregada a la cola. Total en cola: {len(cola_mediciones)}")

except serial.SerialException as e:
    print(f"❌ Error al abrir {puerto_serie}: {e}")
except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Guardando el buffer en archivo...")
