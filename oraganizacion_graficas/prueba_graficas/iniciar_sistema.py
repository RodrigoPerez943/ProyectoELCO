import os
import subprocess
import time
import signal
import sys

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"🔄 Iniciando sistema de adquisición y graficado en la Raspberry Pi...\n📂 Directorio base: {BASE_DIR}")

# Definir rutas absolutas de los scripts
ESCUCHAR_SCRIPT = os.path.join(BASE_DIR, "escuchar_uart.py")
UART_SCRIPT = os.path.join(BASE_DIR, "recolector_uart.py")
GRAFICAS_SCRIPT = os.path.join(BASE_DIR, "actualizar_graficas.py")
DASHBOARD_SCRIPT = os.path.join(BASE_DIR, "dashboard.py")

# Verificar que los archivos existen antes de ejecutarlos
scripts = {
    "Escuchar UART": ESCUCHAR_SCRIPT,
    "Recolector UART": UART_SCRIPT,
    "Actualizar Gráficas": GRAFICAS_SCRIPT,
    "Dashboard Web": DASHBOARD_SCRIPT
}

for nombre, ruta in scripts.items():
    if not os.path.exists(ruta):
        print(f"❌ Error: No se encontró {nombre} ({ruta})")
        sys.exit(1)

# Iniciar scripts en segundo plano
procesos = {}

def iniciar_proceso(nombre, script):
    """Inicia un proceso en segundo plano y lo almacena en el diccionario de procesos."""
    print(f"🚀 Iniciando {nombre}...")
    procesos[nombre] = subprocess.Popen(["python3", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Iniciar procesos necesarios
iniciar_proceso("Escuchar UART", ESCUCHAR_SCRIPT)
time.sleep(2)  # Pequeña espera para asegurar la inicialización

iniciar_proceso("Actualizar Gráficas", GRAFICAS_SCRIPT)
time.sleep(2)

iniciar_proceso("Dashboard Web", DASHBOARD_SCRIPT)

# Manejar interrupción con Ctrl + C
def detener_sistema(signal_received, frame):
    """Finaliza todos los procesos en ejecución de manera ordenada."""
    print("\n🛑 Deteniendo el sistema...")
    for nombre, proceso in procesos.items():
        print(f"🔴 Deteniendo {nombre}...")
        proceso.terminate()
        proceso.wait()
    print("✅ Todos los procesos se han detenido correctamente.")
    sys.exit(0)

# Capturar señales de interrupción (Ctrl + C)
signal.signal(signal.SIGINT, detener_sistema)

# Mantener el script activo hasta que se reciba Ctrl + C
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    detener_sistema(None, None)
