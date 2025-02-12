# La forma en la que llegan los datos es en un formato CSV, en nuestro caso <temperatura>,<humedad>,<timestamp>\n

import serial
import csv
import time

# Configura el puerto serial y la velocidad de baudios (ajusta '/dev/ttyUSB0' según tu conexión)
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Espera a que el puerto se estabilice

# Nombre del archivo CSV donde se almacenarán los datos
csv_filename = 'sensor_data.csv'

# Abre el archivo en modo 'append' para no sobrescribir datos anteriores
with open(csv_filename, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # (Opcional) Escribe el encabezado si el archivo está vacío
    csv_writer.writerow(['Temperatura', 'Humedad', 'Timestamp'])
    
    try:
        while True:
            # Lee una línea del puerto serial
            line = ser.readline().decode('utf-8').strip()
            if line:
                print("Datos recibidos:", line)
                
                # Separa los valores por la coma
                data = line.split(',')
                if len(data) == 3:
                    # Escribe la fila en el archivo CSV
                    csv_writer.writerow(data)
                else:
                    print("Formato de datos inesperado:", data)
    except KeyboardInterrupt:
        print("Terminando la captura de datos.")
    finally:
        ser.close()


