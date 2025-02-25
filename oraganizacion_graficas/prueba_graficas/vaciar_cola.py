import os
import json
import csv
from collections import deque

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivos clave
BUFFER_FILE = os.path.join(BASE_DIR, "buffer_uart.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")

# Cola en memoria (simulando `deque` usada en `escuchar_uart.py`)
TAMANO_COLA = 20  # Ajusta según sea necesario
cola_mediciones = deque(maxlen=TAMANO_COLA)

def cargar_buffer():
    """ Carga las mediciones almacenadas en el buffer JSON """
    if not os.path.exists(BUFFER_FILE):
        return []
    try:
        with open(BUFFER_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("⚠️ Error al leer el buffer. Posible corrupción de datos.")
        return []

def guardar_en_csv(mediciones):
    """ Guarda las mediciones en el archivo CSV """
    if not mediciones:
        print("⚠️ No hay datos en la cola para procesar.")
        return

    # Verificar si el CSV ya existe o necesita encabezado
    existe_csv = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not existe_csv:
            writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
        
        writer.writerows(mediciones)

    print(f"✅ {len(mediciones)} mediciones procesadas y guardadas en el CSV.")

def vaciar_cola():
    """ Vacía la cola de memoria y guarda los datos pendientes """
    print("🛑 Procesando datos pendientes en la memoria...")

    # Procesar datos en `deque`
    mediciones_pendientes = list(cola_mediciones)
    cola_mediciones.clear()  # Vaciar memoria tras guardar los datos

    # Procesar datos del buffer (JSON)
    buffer_pendiente = cargar_buffer()
    
    # Unir ambos conjuntos de datos
    todas_las_mediciones = mediciones_pendientes + buffer_pendiente

    # Guardar en CSV
    guardar_en_csv(todas_las_mediciones)

    # Vaciar buffer JSON
    with open(BUFFER_FILE, "w") as file:
        json.dump([], file)

    print("✅ Cola y buffer vaciados completamente.")

if __name__ == "__main__":
    vaciar_cola()
