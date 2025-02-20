import os
import time
import random
import serial
import subprocess
import serial.tools.list_ports

# Configuración de los puertos virtuales
PUERTO_SIMULADOR = "COM10"
PUERTO_RECOLECTOR = "COM11"
BAUDRATE = 9600

# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo de bandera para indicar modo simulado
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")

# Rutas de los scripts
INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.sh")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.sh")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")


def verificar_puertos():
    """ Verifica si los puertos COM10 y COM11 existen en el sistema. """
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    return PUERTO_SIMULADOR in puertos and PUERTO_RECOLECTOR in puertos


def iniciar_puertos_virtuales():
    """ Ejecuta setup_puertos_virtuales.py para configurar los puertos en VSPE. """
    print("🔧 Verificando y creando puertos virtuales...")
    
    try:
        subprocess.run(["python", SETUP_PUERTOS_SCRIPT], check=True)
        print("✅ Puertos virtuales configurados correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar {SETUP_PUERTOS_SCRIPT}: {e}")


def esperar_puertos():
    """ Espera hasta que los puertos COM10 y COM11 sean detectados por el sistema. """
    print("⏳ Esperando a que Windows registre los puertos COM10 y COM11...")
    for _ in range(10):  # Espera hasta 10 intentos (aprox. 10 segundos)
        if verificar_puertos():
            print("✅ Puertos detectados correctamente.")
            return True
        time.sleep(1)
    print("❌ Los puertos no fueron detectados a tiempo.")
    return False


def iniciar_sistema():
    """ Inicia el sistema y el recolector de datos """
    print("🚀 Iniciando sistema simulado...")

    # Ejecutar el script de inicialización
    subprocess.Popen(["bash", INICIAR_SCRIPT], cwd=BASE_DIR)

    # Abrir recolector_uart.py en una nueva terminal de Windows
    recolector_cmd = f'start cmd /k "python {os.path.join(BASE_DIR, "recolector_uart.py")} {PUERTO_RECOLECTOR}"'
    subprocess.Popen(recolector_cmd, shell=True)


def detener_sistema():
    """ Detiene el sistema y archiva los datos """
    print("🛑 Deteniendo el sistema y archivando datos...")
    subprocess.run(["bash", DETENER_SCRIPT], cwd=BASE_DIR, check=True)

    # Eliminar el archivo de bandera de simulación
    if os.path.exists(SIM_FLAG):
        os.remove(SIM_FLAG)
        print("✅ Modo simulado desactivado.")


# ✅ Ejecutar `setup_puertos_virtuales.py` antes de iniciar la simulación
iniciar_puertos_virtuales()

# ✅ Esperar a que los puertos virtuales estén listos
if not esperar_puertos():
    print("❌ No se pudo continuar porque los puertos virtuales no fueron detectados.")
    exit(1)

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
