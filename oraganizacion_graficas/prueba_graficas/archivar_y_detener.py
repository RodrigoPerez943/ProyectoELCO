import os
import time
import shutil
import subprocess

# Definir rutas de los archivos y scripts
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ESC_UAR_SCRIPT = os.path.join(BASE_DIR, "escuchar_uart.py")
GRAFICADOR_SCRIPT = os.path.join(BASE_DIR, "actualizar_graficas.py")
VACIAR_COLA_SCRIPT = os.path.join(BASE_DIR, "vaciar_cola.py")
GRAFICAR_PENDIENTES_SCRIPT = os.path.join(BASE_DIR, "graficar_pendientes.py")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
PNG_DIR = os.path.join(BASE_DIR, "graficas_png")
MAT_DIR = os.path.join(BASE_DIR, "graficas_mat")

print("🛑 Deteniendo el sistema y archivando datos...")

# **1️⃣ Enviar señal de detención a `escuchar_uart.py`**
print("📢 Enviando señal de detención a escuchar_uart.py...")
subprocess.run(["pkill", "-f", "escuchar_uart.py"], stderr=subprocess.DEVNULL)

# **2️⃣ Esperar a que `escuchar_uart.py` termine de procesar la cola**
print("⏳ Esperando a que escuchar_uart.py termine de procesar la cola...")
time.sleep(2)

# **3️⃣ Ejecutar `vaciar_cola.py` para procesar mediciones pendientes**
print("📂 Procesando mediciones almacenadas en la cola...")
subprocess.run(["python", VACIAR_COLA_SCRIPT])

# **4️⃣ Esperar a que `graficar_pendientes.py` actualice las gráficas**
print("📊 Esperando a que se actualicen las gráficas con datos pendientes...")
subprocess.run(["python", GRAFICAR_PENDIENTES_SCRIPT])

# **5️⃣ Forzar cierre de `actualizar_graficas.py` si sigue corriendo**
proc = subprocess.run(["pgrep", "-f", "actualizar_graficas.py"], stdout=subprocess.PIPE, text=True)
if proc.stdout.strip():
    print("⚠️ El proceso de graficado sigue activo, forzando su cierre...")
    subprocess.run(["pkill", "-f", "actualizar_graficas.py"])

print("✅ Graficador finalizado con éxito.")

# **6️⃣ Mover archivos a backup**
FECHA = time.strftime("%Y-%m-%d_%H-%M-%S")
ARCHIVO_DIR = os.path.join(BASE_DIR, f"backup_{FECHA}")
os.makedirs(ARCHIVO_DIR, exist_ok=True)

if os.path.exists(PNG_DIR):
    shutil.move(PNG_DIR, os.path.join(ARCHIVO_DIR, "graficas_png"))
    print("📁 Carpetas de imágenes PNG movidas a backup.")

if os.path.exists(MAT_DIR):
    shutil.move(MAT_DIR, os.path.join(ARCHIVO_DIR, "graficas_mat"))
    print("📁 Carpetas de imágenes MAT movidas a backup.")

print(f"✅ Archivos de gráficas movidos a: {ARCHIVO_DIR}")

# **7️⃣ Eliminar el CSV después de archivar**
if os.path.exists(CSV_FILE):
    os.remove(CSV_FILE)
    print("🗑️ Archivo CSV eliminado correctamente.")
else:
    print("⚠️ No se encontró sensor_data.csv.")

print("✅ Sistema detenido y datos archivados.")
