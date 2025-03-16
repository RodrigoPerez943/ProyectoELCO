import serial
import time
import json
import os

# Configuración UART
UART_PORT = "/dev/ttyS0"  # ⚠️ Ajustar según el sistema
BAUDRATE = 9600
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def cargar_config():
    """ Cargar la configuración desde el archivo config.json """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"intervalo": 10}

def enviar_comando_uart(mensaje):
    """ Enviar un comando por UART """
    try:
        with serial.Serial(UART_PORT, BAUDRATE, timeout=1) as ser:
            ser.write(mensaje.encode())
            print(f"📡 Enviado por UART: {mensaje.strip()}")
    except Exception as e:
        print(f"❌ Error enviando por UART: {e}")

def monitorear_intervalo():
    """ Monitorea si el usuario cambia el intervalo y lo envía a los nodos """
    intervalo_actual = cargar_config()["intervalo"]
    
    while True:
        nueva_config = cargar_config()
        nuevo_intervalo = nueva_config.get("intervalo", 10)

        if nuevo_intervalo != intervalo_actual:
            print(f"🔄 Intervalo cambiado: {nuevo_intervalo}s")
            enviar_comando_uart(f"INTERVALO:{nuevo_intervalo}\n")
            intervalo_actual = nuevo_intervalo

        time.sleep(2)  # Revisar cada 2 segundos si hay cambios

if __name__ == "__main__":
    print("📡 Control UART iniciado...")
    monitorear_intervalo()
