import os
import time
import random
import serial
import subprocess
import json
import threading  # Para escuchar UART en un hilo separado

# 📌 Configuración de UART
PUERTO_LECTURA = "COM8"  # 📥 Recibe el intervalo
PUERTO_ESCRITURA = "COM10"  # 📤 Envía las mediciones
BAUDRATE = 9600  # Velocidad UART

# 📌 Archivos y rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERVALO_FILE = os.path.join(BASE_DIR, "intervalo_config.json")  # 📂 Intervalo guardado desde la web
SIM_FLAG = os.path.join(BASE_DIR, "sim_mode.flag")  # Bandera de simulación

INICIAR_SCRIPT = os.path.join(BASE_DIR, "iniciar_sistema.py")
DETENER_SCRIPT = os.path.join(BASE_DIR, "archivar_y_detener.py")
SETUP_PUERTOS_SCRIPT = os.path.join(BASE_DIR, "setup_puertos_virtuales.py")

# 📌 Estado inicial del intervalo (No empieza hasta recibirlo)
intervalo_entre_envios = None
lock = threading.Lock()  # 🔒 Para sincronizar cambios en el intervalo

# ✅ Crear archivo de simulación
with open(SIM_FLAG, "w") as f:
    f.write("SIMULATION MODE ACTIVE")
print(f"✅ Modo simulación activado: {SIM_FLAG}")

# ✅ Generar direcciones MAC aleatorias simuladas
def generar_mac_aleatoria():
    return ":".join(f"{random.randint(0x00, 0xFF):02X}" for _ in range(6))

mac_sensores = [generar_mac_aleatoria() for _ in range(4)]
mac_fuera = generar_mac_aleatoria()
print(f"📡 MAC de los sensores interiores: {mac_sensores}")
print(f"🌳 MAC del sensor exterior: {mac_fuera}")

# ✅ Obtener intervalo guardado en la configuración web
def obtener_intervalo():
    """Lee el intervalo desde el archivo JSON."""
    if os.path.exists(INTERVALO_FILE):
        with open(INTERVALO_FILE, "r") as file:
            data = json.load(file)
            return data.get("intervalo", None)
    return None

# ✅ Escuchar cambios en el intervalo desde UART en segundo plano
def escuchar_intervalo():
    """Escucha UART (COM8) y actualiza el intervalo en tiempo real."""
    global intervalo_entre_envios
    try:
        with serial.Serial(PUERTO_LECTURA, BAUDRATE, timeout=1) as uart:
            while True:
                if uart.in_waiting > 0:
                    linea = uart.readline().decode().strip()
                    if linea.startswith("INTERVALO:"):
                        nuevo_intervalo = int(linea.split(":")[1])
                        if nuevo_intervalo > 0:
                            with lock:  # 🔒 Bloquear acceso al intervalo
                                intervalo_entre_envios = nuevo_intervalo
                            print(f"⏳ Intervalo actualizado desde UART: {intervalo_entre_envios} segundos")
    except Exception as e:
        print(f"⚠️ Error al leer desde UART: {e}")
# ✅ Iniciar el sistema y los scripts necesarios
def iniciar_sistema():
    """Inicia los procesos necesarios."""
    print("🚀 Iniciando sistema simulado...")
    subprocess.Popen(["python", INICIAR_SCRIPT])
iniciar_sistema()
# ✅ Esperar hasta que el usuario ajuste un intervalo en la web
while intervalo_entre_envios is None:
    print("⏳ Esperando que el usuario configure un intervalo en la web...")
    intervalo_entre_envios = obtener_intervalo()
    time.sleep(2)

print(f"✅ Intervalo inicial recibido: {intervalo_entre_envios} segundos")



# ✅ Detener el sistema
def detener_sistema():
    """Detiene el sistema y archiva datos."""
    print("🛑 Deteniendo el sistema y archivando datos...")
    subprocess.run(["python", DETENER_SCRIPT])
    if os.path.exists(SIM_FLAG):
        os.remove(SIM_FLAG)
        print("✅ Modo simulado desactivado.")

# ✅ Iniciar hilo para escuchar cambios en UART sin bloquear el bucle principal
threading.Thread(target=escuchar_intervalo, daemon=True).start()

# ✅ Simulación de datos UART enviando hasta 4 sensores simultáneamente
try:
    with serial.Serial(PUERTO_ESCRITURA, BAUDRATE, timeout=1) as uart:
        while True:
            with lock:  # 🔒 Obtener el último intervalo actualizado
                intervalo_actual = intervalo_entre_envios

            # 🌳 Enviar medición exterior (ext=1)
            temperature = round(random.uniform(10, 15), 1)
            medicion_fuera = f"{mac_fuera},{temperature},{0},{0},1\n"
            uart.write(medicion_fuera.encode())
            print(f"📡 EXTERIOR: {medicion_fuera}")
            time.sleep(0.05)

            # 📡 Enviar mediciones interiores (ext=0)
            num_sensores = random.randint(1, 4)
            for i in range(num_sensores):
                mac_actual = mac_sensores[i]
                temperature = round(random.uniform(20, 25), 1)
                humidity = round(random.uniform(40, 60), 2)
                pressure = round(random.uniform(900, 1100), 2)

                medicion_total = f"{mac_actual},{temperature},{humidity},{pressure},0\n"
                uart.write(medicion_total.encode())
                print(f"📡 INTERIOR: {medicion_total}")
                time.sleep(0.05)

            print(f"⏳ Esperando {intervalo_actual} segundos antes del siguiente envío...")
            time.sleep(intervalo_actual)

except KeyboardInterrupt:
    print("\n🛑 Se detectó interrupción. Deteniendo el sistema...")
    detener_sistema()
