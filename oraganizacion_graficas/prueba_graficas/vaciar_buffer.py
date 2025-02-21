import os
import json
import time

BUFFER_FILE = "buffer_uart.json"

print("🔄 Vaciando buffer antes de cerrar el sistema...")

try:
    while True:
        if os.path.exists(BUFFER_FILE):
            with open(BUFFER_FILE, "r") as file:
                try:
                    buffer_mediciones = json.load(file)
                except json.JSONDecodeError:
                    buffer_mediciones = []

        if buffer_mediciones:
            print(f"✅ Procesando {len(buffer_mediciones)} mediciones pendientes...")
            buffer_mediciones.clear()

            with open(BUFFER_FILE, "w") as file:
                json.dump(buffer_mediciones, file, indent=4)

            time.sleep(1)  # Pequeña pausa para asegurar que se escribe correctamente
        else:
            print("✅ Buffer vacío. Saliendo del proceso.")
            break

except KeyboardInterrupt:
    print("\n🛑 Interrupción detectada. Guardando buffer actual...")
    with open(BUFFER_FILE, "w") as file:
        json.dump(buffer_mediciones, file, indent=4)
    print("🔚 Proceso de vaciado de buffer detenido.")
