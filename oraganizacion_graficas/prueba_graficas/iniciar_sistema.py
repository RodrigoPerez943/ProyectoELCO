import os
import sys
import time
import subprocess

def encontrar_ruta(script):
    """ Devuelve la ruta absoluta de un script dentro del directorio base. """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, script)

# Definir rutas de los scripts
SCRIPTS = {
    "database": encontrar_ruta("database.py"),
    "escuchar_uart": encontrar_ruta("escuchar_uart.py"),
    "recolector_uart": encontrar_ruta("recolector_uart.py"),
    "actualizar_graficas": encontrar_ruta("actualizar_graficas.py"),
    "dashboard": encontrar_ruta("dashboard.py"),
}

# Verificar que los archivos existen antes de ejecutarlos
for nombre, ruta in SCRIPTS.items():
    if not os.path.isfile(ruta):
        print(f"❌ Error: No se encontró {ruta}")
        sys.exit(1)

# Iniciar scripts en segundo plano
print("🔄 Iniciando sistema de adquisición y graficado...")
subprocess.Popen(["python", SCRIPTS["database"]])

print("📡 Iniciando escucha de datos UART...")
subprocess.Popen(["python", SCRIPTS["escuchar_uart"]])

time.sleep(5)  # Esperar a que UART comience a recibir datos

print("📊 Iniciando actualización de gráficas...")
subprocess.Popen(["python", SCRIPTS["actualizar_graficas"]])

print("🖥️ Iniciando dashboard web...")
subprocess.Popen(["python", SCRIPTS["dashboard"]])

# Mantener el script en ejecución para evitar que finalice
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Sistema detenido manualmente.")
    sys.exit(0)
