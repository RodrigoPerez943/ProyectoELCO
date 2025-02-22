import json
import csv
import os
import time

# Definir rutas de archivos
BUFFER_FILE = "buffer_uart.json"
CSV_FILE = "sensor_data.csv"

print("📤 Procesando la cola en memoria y guardando en CSV...")

# Verificar si hay un buffer
if os.path.exists(BUFFER_FILE):
    with open(BUFFER_FILE, "r") as file:
        buffer_mediciones = json.load(file)

    if buffer_mediciones:
        print(f"✅ Procesando {len(buffer_mediciones)} mediciones almacenadas.")

        # Guardar en CSV
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            for medicion in buffer_mediciones:
                writer.writerow(medicion)

        # Vaciar el buffer
        with open(BUFFER_FILE, "w") as file:
            json.dump([], file)

        print("✅ Todas las mediciones han sido procesadas y guardadas.")
    else:
        print("⚠️ No hay mediciones pendientes en el buffer.")
else:
    print("⚠️ No se encontró el archivo de buffer.")

print("🛑 Cola de memoria vaciada correctamente.")
