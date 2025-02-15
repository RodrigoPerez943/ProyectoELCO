import csv
import random
import time

def generate_sensor_data(filename="sensor_data.csv"):
    nodes = [1, 2, 3]  # Tres nodos
    entries_per_node = 120
    initial_temperature = 24.5
    initial_humidity = 55.2
    initial_pressure = 1000  # Presión en hPa
    timestamp_start = int(time.time())  # Timestamp actual
    interval = 15  # Intervalo de 15 segundos entre mediciones

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["temperature", "humidity", "timestamp", "node_id", "pressure"])
        
        for node_id in nodes:
            temperature = initial_temperature
            humidity = initial_humidity
            pressure = initial_pressure
            timestamp = timestamp_start
            
            for _ in range(entries_per_node):
                writer.writerow([round(temperature, 1), round(humidity, 1), timestamp, node_id, round(pressure, 1)])
                
                # Variaciones lógicas para cada medición
                temperature -= random.uniform(0.01, 0.1)  # Decremento progresivo
                humidity += random.uniform(-0.5, 0.5)  # Fluctuaciones en humedad
                pressure += random.uniform(-0.3, 0.3)  # Pequeñas variaciones en la presión
                timestamp += interval  # Incremento del tiempo

if __name__ == "__main__":
    generate_sensor_data()
    print("Archivo CSV generado con éxito.")