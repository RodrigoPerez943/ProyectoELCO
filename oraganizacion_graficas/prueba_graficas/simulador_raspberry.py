import os
import time
import random
import serial
import subprocess

# Configuración de UART
PUERTO_SERIE = "COM10"  # Puerto UART en Windows
BAUDRATE = 9600  # Mantener en 9600 para ser compatible con Raspberry Pi

# Obtener la ruta del directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas de los scripts
INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.py")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.py")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")  # Archivo de control

with open(SIM_FLAG, "w") as f:
    f.write("SIMULATION MODE ACTIVE")
print(f"✅ Archivo de simulación creado en: {SIM_FLAG}")

# Generar direcciones MAC aleatorias simuladas para hasta 4 sensores
def generar_mac_aleatoria():
    """ Genera una dirección MAC aleatoria con el formato XX:XX:XX:XX:XX:XX """
    return ":".join(f"{random.randint(0x00, 0xFF):02X}" for _ in range(6))

mac_sensores = [generar_mac_aleatoria() for _ in range(4)]
print(f"📡 MAC de los sensores simulados: {mac_sensores}")

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
    subprocess.Popen(["python", INICIAR_SCRIPT])

# Detener el sistema
def detener_sistema():
    """ Detiene el sistema y archiva los datos """
    print("🛑 Deteniendo el sistema y archivando datos...")
    subprocess.run(["python", DETENER_SCRIPT])

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
time.sleep(5)

# ✅ Simulación de datos UART enviando hasta 4 sensores simultáneamente en una sola línea
try:
    with serial.Serial(PUERTO_SERIE, BAUDRATE, timeout=1) as uart:
        while True:
            num_sensores = random.randint(1, 4)  # Enviar datos de entre 1 y 4 sensores en cada ciclo

            for i in range(num_sensores):
                mac_actual = mac_sensores[i]
                temperature = round(random.uniform(20, 25), 1)
                humidity = round(random.uniform(40, 60), 2)
                pressure = round(random.uniform(900, 1100), 2)
                ext = round(random.uniform(0, 10), 2)

                # Formato correcto en una sola línea: MAC, Temp, Hum, Presión, Ext
                medicion_total =f"{mac_actual},{temperature},{humidity},{pressure},{ext}\n"
                uart.write(medicion_total.encode())
                print(f"📡 Simulador UART: Enviando -> {medicion_total}")
                time.sleep(0.05)

            time.sleep(5)  # Pequeña espera entre envíos

except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Deteniendo el sistema...")
    detener_sistema()
