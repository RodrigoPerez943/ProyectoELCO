import os
import time
import random
import serial
import subprocess

# Configurar los puertos virtuales (deben coincidir con `setup_puertos_virtuales.py`)
PUERTO_SIMULADOR = "COM10"
PUERTO_RECOLECTOR = "COM11"
BAUDRATE = 9600

# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo de bandera para indicar modo simulado
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")

# Rutas de los scripts de shell y de setup
INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.sh")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.sh")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")

# ✅ Crear los puertos virtuales antes de iniciar la simulación
def iniciar_puertos_virtuales():
    print("🔧 Creando puertos virtuales con setup_puertos_virtuales.py...")
    subprocess.run(["python", SETUP_PUERTOS_SCRIPT], check=True)

    # Espera para que Windows registre los puertos
    time.sleep(5)

# ✅ Iniciar los scripts necesarios
def iniciar_sistema():
    print("🚀 Iniciando sistema simulado...")

    # Ejecutar el script de inicialización
    subprocess.Popen(["bash", INICIAR_SCRIPT], cwd=BASE_DIR)

    # Abrir recolector_uart.py en una nueva terminal de Windows
    recolector_cmd = f'start cmd /k "python {os.path.join(BASE_DIR, "recolector_uart.py")} {PUERTO_RECOLECTOR}"'
    subprocess.Popen(recolector_cmd, shell=True)

# ✅ Detener los scripts y limpiar archivos
def detener_sistema():
    print("🛑 Deteniendo el sistema y archivando datos...")
    subprocess.Popen(["bash", DETENER_SCRIPT], cwd=BASE_DIR)

    # Eliminar el archivo de bandera de simulación
    if os.path.exists(SIM_FLAG):
        os.remove(SIM_FLAG)
        print("✅ Modo simulado desactivado.")

# ✅ Ejecutar `setup_puertos_virtuales.py` antes de iniciar
iniciar_puertos_virtuales()

# ✅ Crear el archivo de bandera para indicar modo simulado
with open(SIM_FLAG, "w") as f:
    f.write("SIMULATION MODE ACTIVE")

# ✅ Iniciar el sistema y los scripts necesarios
iniciar_sistema()

# ✅ Simulación de datos UART usando `pyserial`
try:
    with serial.Serial(PUERTO_SIMULADOR, BAUDRATE, timeout=1) as uart:
        while True:
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 60), 2)
            pressure = round(random.uniform(900, 1100), 2)
            timestamp = int(time.time())
            node_id = random.randint(1, 3)

            medida = f"{temperature},{humidity},{timestamp},{node_id},{pressure}\n"
            uart.write(medida.encode())

            print(f"📡 Simulador UART: Enviando -> {medida.strip()}")
            time.sleep(5)
except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Deteniendo el sistema...")
    detener_sistema()
