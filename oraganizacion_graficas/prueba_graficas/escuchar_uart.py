import os
import time
import serial
import subprocess
import platform
import json
import datetime
from collections import deque

# Configuración UART
PUERTO_SERIE = "COM11"  # Cambia esto según el sistema
#PUERTO_SERIE = /dev/serial0
BAUDRATE = 9600
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_FILE =os.path.join(BASE_DIR, "buffer_uart.json")   # Archivo para almacenar datos pendientes

# Tamaño de la memoria y lote de procesamiento
TAMANO_MEMORIA = 20
TAMANO_LOTE = 5
cola_mediciones = deque(maxlen=TAMANO_MEMORIA)

# Detección del sistema operativo para usar Python adecuado
sistema_operativo = platform.system()

RECOLECTOR_SCRIPT = os.path.join(BASE_DIR, "recolector_uart.py")
COMANDO_PROCESAR = ["python", RECOLECTOR_SCRIPT] if sistema_operativo != "Windows" else ["python", RECOLECTOR_SCRIPT]

def enviar_a_recolector():
    """ Envía las mediciones a recolector_uart cuando se alcanza el tamaño del lote """
    if len(cola_mediciones) >= TAMANO_LOTE:
        print(f"🚀 Enviando {len(cola_mediciones)} mediciones a recolector_uart.py")

        # Guardar las mediciones en buffer
        with open(BUFFER_FILE, "w") as file:
            json.dump(list(cola_mediciones), file, indent=4)

        # Llamar a recolector_uart.py para procesar los datos
        subprocess.run(COMANDO_PROCESAR)

        # Vaciar la cola en memoria después de enviarla
        cola_mediciones.clear()

try:
    with serial.Serial(PUERTO_SERIE, BAUDRATE, timeout=1) as uart:
        print(f"📡 Escuchando UART en {PUERTO_SERIE}...")

        while True:
            try:
                datos = uart.readline().decode(errors="ignore").strip()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") 
                if not datos:
                    continue  # Si no hay datos, continuar

                print(f"📡 Recibido -> {datos}")

                # Separar valores
                partes = datos.split(",")
                if len(partes) != 5:
                    print(f"⚠️ Formato incorrecto recibido: {datos} (Esperados: 5, Recibidos: {len(partes)})")
                    continue

                # Obtener timestamp en el momento exacto de la recepción
                

                # Agregar la medición a la cola en memoria
                medicion = [timestamp] + [p.strip() for p in partes]
                cola_mediciones.append(medicion)
                print(f"📥 Medición añadida: {len(cola_mediciones)} en memoria / {TAMANO_MEMORIA}")

                # Si se alcanza el tamaño del lote, enviar a recolector
                enviar_a_recolector()

            except Exception as e:
                print(f"⚠️ Error en la lectura de UART: {e}")

            time.sleep(0.05)  # Pequeña espera para evitar sobrecarga

except serial.SerialException as e:
    print(f"❌ Error al abrir UART: {e}")
