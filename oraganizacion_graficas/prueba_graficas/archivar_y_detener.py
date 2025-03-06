import os
import json
import shutil
import platform
import time
import subprocess

# Directorios y archivos clave
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_FILE = os.path.join(BASE_DIR, "buffer_uart.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
MAT_DIR = os.path.join(BASE_DIR, "graficas_mat")
PNG_DIR = os.path.join(BASE_DIR, "graficas_png")
BACKUP_DIR = os.path.join(BASE_DIR, f"backup_{time.strftime('%Y-%m-%d_%H-%M-%S')}")

# Detectar sistema operativo
es_linux = platform.system() == "Linux"

def detener_procesos():
    """ Detiene `escuchar_uart.py` y `actualizar_graficas.py` según el sistema operativo """
    comandos = {
        "Windows": ["taskkill", "/F", "/IM", "python.exe"],
        "Linux": ["pkill", "-f", "escuchar_uart.py"]
    }
    try:
        subprocess.run(comandos["Linux" if es_linux else "Windows"], stderr=subprocess.DEVNULL)
        print("✅ Procesos detenidos correctamente.")
    except Exception as e:
        print(f"⚠️ Error al detener procesos: {e}")

def vaciar_buffer():
    """ Procesar medidas pendientes antes de cerrar el sistema """
    print("🛑 Procesando datos pendientes en la cola...")

    # Llamar a `vaciar_cola.py` para procesar cualquier dato en memoria
    try:
        subprocess.run(["python", os.path.join(BASE_DIR, "vaciar_cola.py")], check=True)
        print("✅ Datos en cola vaciados correctamente.")
    except Exception as e:
        print(f"⚠️ Error al vaciar la cola: {e}")

def archivar_graficas():
    """ Mueve las gráficas a la carpeta de backup antes de cerrar """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for carpeta in [MAT_DIR, PNG_DIR]:
        if os.path.exists(carpeta):
            shutil.move(carpeta, os.path.join(BACKUP_DIR, os.path.basename(carpeta)))
            print(f"📁 {carpeta} archivada en {BACKUP_DIR}")

def eliminar_csv():
    """ Elimina el CSV después de vaciar la cola y graficar los datos """
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        print(f"❌ Archivo {CSV_FILE} eliminado después de procesar los datos.")

def generar_graficas_pendientes():
    """ Ejecuta `graficar_pendientes.py` para actualizar las gráficas antes de cerrar """
    print("📊 Generando gráficas pendientes antes de cerrar...")
    try:
        subprocess.run(["python", os.path.join(BASE_DIR, "graficar_pendientes.py")], check=True)
        print("✅ Gráficas pendientes generadas correctamente.")
    except Exception as e:
        print(f"⚠️ Error al generar gráficas pendientes: {e}")

# Ejecutar pasos de cierre
print("🛑 Deteniendo el sistema y archivando datos...")
vaciar_buffer()  # Procesar medidas pendientes
generar_graficas_pendientes()  # Graficar medidas finales
archivar_graficas()  # Mover las gráficas a backup
eliminar_csv()  # Ahora el CSV se elimina en lugar de moverse
detener_procesos()  # Apagar los procesos en ejecución
print("✅ Sistema detenido completamente.")
