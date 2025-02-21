import os
import time
import random
import serial
import subprocess

# Configuración de UART
PUERTO_SIMULADOR = "COM10"  # Puerto de simulación en Windows (VSPE)
PUERTO_REAL = "/dev/serial0"  # UART real en Raspberry Pi
BAUDRATE = 9600


# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de los scripts
INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.sh")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.sh")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")  # Se crea en el directorio de ejecución



with open(SIM_FLAG, "w") as f:
    f.write("SIMULATION MODE ACTIVE")

print(f"✅ Archivo de simulación creado en: {SIM_FLAG}")



# Determinar si estamos en simulación o en hardware real
def es_modo_simulado():
    return os.path.exists(SIM_FLAG)

if es_modo_simulado():
    puerto_serie = PUERTO_SIMULADOR
    print("🟡 Modo SIMULADO detectado. Usando puerto virtual:", PUERTO_SIMULADOR)
else:
    # En una Raspberry Pi, usar el puerto real `/dev/serial0` o `/dev/ttyS0`
    puerto_serie = PUERTO_REAL if os.path.exists(PUERTO_REAL) else "/dev/ttyS0"
    print("🟢 Modo REAL detectado. Usando puerto UART:", puerto_serie)

# Generar una dirección MAC aleatoria simulada
def generar_mac_aleatoria():
    """ Genera una dirección MAC aleatoria con el formato XX:XX:XX:XX:XX:XX """
    return ":".join(f"{random.randint(0x00, 0xFF):02X}" for _ in range(6))

# Determinar qué puerto usar (simulación vs UART real)

# Asignar una dirección MAC simulada


# Ejecutar `setup_puertos_virtuales.py` antes de iniciar la simulación
def iniciar_puertos_virtuales():
    """ Ejecuta setup_puertos_virtuales.py para configurar los puertos en VSPE. """
    print("🔧 Verificando y creando puertos virtuales...")
    
    try:
        subprocess.run(["python", SETUP_PUERTOS_SCRIPT], check=True)
        print("✅ Puertos virtuales configurados correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar {SETUP_PUERTOS_SCRIPT}: {e}")

# Esperar a que los puertos COM sean detectados en el sistema
def esperar_puertos():
    """ Espera hasta que los puertos sean detectados por el sistema. """
    print("⏳ Esperando a que Windows registre los puertos virtuales...")
    for _ in range(10):  # Espera hasta 10 intentos (~10 segundos)
        try:
            with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as _:
                print("✅ Puertos detectados correctamente.")
                return True
        except serial.SerialException:
            time.sleep(1)
    print("❌ Los puertos no fueron detectados a tiempo.")
    return False

# Iniciar el sistema
def iniciar_sistema():
    """ Inicia el sistema y los procesos necesarios """
    print("🚀 Iniciando sistema simulado...")

    # Ejecutar el script de inicialización
    subprocess.Popen(["bash", INICIAR_SCRIPT], cwd=BASE_DIR)

# Detener el sistema
def detener_sistema():
    """ Detiene el sistema y archiva los datos """
    print("🛑 Deteniendo el sistema y archivando datos...")
    subprocess.run(["bash", DETENER_SCRIPT], cwd=BASE_DIR, check=True)

    # Eliminar el archivo de bandera de simulación
    if os.path.exists(SIM_FLAG):
        os.remove(SIM_FLAG)
        print("✅ Modo simulado desactivado.")



# ✅ Esperar a que los puertos virtuales estén listos
if not esperar_puertos():
    print("❌ No se pudo continuar porque los puertos virtuales no fueron detectados.")
    exit(1)


mac_simulada = generar_mac_aleatoria()

# ✅ Ejecutar `setup_puertos_virtuales.py` antes de iniciar la simulación
iniciar_puertos_virtuales()

iniciar_sistema()

# ✅ Simulación de datos UART usando `pyserial`
try:
    with serial.Serial(puerto_serie, BAUDRATE, timeout=1) as uart:
        while True:
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 60), 2)
            pressure = round(random.uniform(900, 1100), 2)


            # 🔹 Enviar los datos en el orden correcto: temperatura, humedad, timestamp, MAC, presión
            medida = f"{temperature},{humidity},{mac_simulada},{pressure}\n"
            uart.write(medida.encode())

            print(f"📡 Simulador UART: Enviando -> {medida.strip()}")
            time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Deteniendo el sistema...")
    detener_sistema()
