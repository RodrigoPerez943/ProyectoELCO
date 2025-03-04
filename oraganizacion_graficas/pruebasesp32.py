import serial
import time

# Configurar UART en la Raspberry Pi
ser = serial.Serial('/dev/serial0', 115200, timeout=1)

print("Esperando datos del ESP32-C3...")

while True:
    try:
        data = ser.readline().decode('utf-8').strip()
        if data:
            print("Datos recibidos:", data)
    except Exception as e:
        print("Error en la lectura:", e)
    time.sleep(0.1)
