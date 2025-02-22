import os
import time
import random
import serial
import subprocess

# Configuración de UART
PUERTO_SERIE = "COM10"  # Puerto UART a utilizar en Windows (VSPE)
BAUDRATE = 9600  # Mantener en 9600 para ser compatible con Raspberry Pi


# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de los scripts
INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.sh")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.sh")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag") # Archivo de control

with open(SIM_FLAG, "w") as f:
    f.write("SIMULATION MODE ACTIVE")
print(f"✅ Archivo de simulación creado en: {SIM_FLAG}")

# Generar una dirección MAC aleatoria simulada
def generar_mac_aleatoria():
    """ Genera una dirección MAC aleatoria con el formato XX:XX:XX:XX:XX:XX """
    return ":".join(f"{random.randint(0x00, 0xFF):02X}" for _ in range(6))

# Asignar una dirección MAC simulada
mac_simulada = generar_mac_aleatoria()
print(f"📡 MAC del sensor simulado: {mac_simulada}")

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
            with serial.Serial(PUERTO_SERIE, BAUDRATE, timeout=1) as _:
                print("✅ Puerto detectado correctamente.")
                return True
        except serial.SerialException:
            time.sleep(1)
    print("❌ El puerto no fue detectado a tiempo.")
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

# ✅ Ejecutar `setup_puertos_virtuales.py` antes de iniciar la simulación
iniciar_puertos_virtuales()

# ✅ Esperar a que el puerto virtual esté listo
if not esperar_puertos():
    print("❌ No se pudo continuar porque el puerto virtual no fue detectado.")
    exit(1)




# ✅ Iniciar el sistema y los scripts necesarios
iniciar_sistema()

# ✅ Simulación de datos UART enviando en orden, pero en mensajes separados
try:
    with serial.Serial(PUERTO_SERIE, BAUDRATE, timeout=1) as uart:
        while True:
            # 🔹 Se envía cada dato de manera secuencial
            uart.write(f"MAC: {mac_simulada}\n".encode())
            print(f"📡 Simulador UART: Enviando -> MAC: {mac_simulada}")
            time.sleep(0.01)  # Pequeño delay

            temperature = round(random.uniform(20, 30), 2)
            uart.write(f"T: {temperature}\n".encode())
            print(f"📡 Simulador UART: Enviando -> T: {temperature}")
            time.sleep(0.01)

            humidity = round(random.uniform(40, 60), 2)
            uart.write(f"H: {humidity}\n".encode())
            print(f"📡 Simulador UART: Enviando -> H: {humidity}")
            time.sleep(0.01)

            pressure = round(random.uniform(900, 1100), 2)
            uart.write(f"p: {pressure}\n".encode())
            print(f"📡 Simulador UART: Enviando -> p: {pressure}")
            time.sleep(0.01)

            ext = round(random.uniform(0, 10), 2)
            uart.write(f"EXT: {ext}\n".encode())
            print(f"📡 Simulador UART: Enviando -> EXT: {ext}")
            time.sleep(0.01)

            time.sleep(0.003)

except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Deteniendo el sistema...")
    detener_sistema()
