import serial
import csv
import os

# Configuración del puerto UART
PORT = "/dev/serial0"  # Ajusta según tu configuración
BAUDRATE = 9600  # Ajusta la velocidad según tu sensor
CSV_FILE = "sensor_data.csv"

# Iniciar conexión serie
ser = serial.Serial(PORT, BAUDRATE, timeout=None)  # Espera indefinidamente hasta recibir datos

# Crear el archivo CSV si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["temperature", "humidity", "timestamp", "node_id", "pressure"])

print("📡 Esperando datos UART...")

while True:
    try:
        # Leer línea del puerto serie (bloqueante, espera hasta recibir datos)
        linea = ser.readline().decode("utf-8").strip()

        if linea:
            # Suponiendo que los datos llegan en el formato: "temp,hum,timestamp,node,press"
            datos = linea.split(",")

            if len(datos) == 5:
                try:
                    temperature = float(datos[0])
                    humidity = float(datos[1])
                    timestamp = int(datos[2])
                    node_id = int(datos[3])
                    pressure = float(datos[4])

                    # Guardar en el CSV
                    with open(CSV_FILE, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([temperature, humidity, timestamp, node_id, pressure])

                    print(f"✅ Medida guardada: {temperature}°C, {humidity}%, {timestamp}, Nodo {node_id}, {pressure} hPa")

                except ValueError:
                    print("⚠️ Error: Datos inválidos recibidos.")

    except Exception as e:
        print(f"⚠️ Error en UART: {e}")
