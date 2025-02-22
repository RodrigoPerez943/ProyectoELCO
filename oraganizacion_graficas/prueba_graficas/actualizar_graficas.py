import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.io as sio
import time

CSV_FILE = "sensor_data.csv"
MAT_DIR = "graficas_mat"
PNG_DIR = "graficas_png"

# Crear carpetas si no existen
os.makedirs(MAT_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

print("\U0001F4CA Monitoreando el archivo CSV para actualizar las gráficas...")

# Estado previo del CSV
last_timestamp = {}

while True:
    try:
        # Leer los datos actuales
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            print("⚠️ No hay datos en el archivo CSV. Esperando nuevas mediciones...")
            time.sleep(5)
            continue

        # Obtener nodos únicos
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]

            # Crear carpeta específica para el nodo
            nodo_dir = os.path.join(PNG_DIR, f"nodo_{node_id}")
            os.makedirs(nodo_dir, exist_ok=True)

            # Verificar si hay nuevas medidas comparando con el último timestamp guardado
            if node_id in last_timestamp and last_timestamp[node_id] >= data_node["timestamp"].max():
                continue  # No hay nuevos datos, pasamos al siguiente nodo

            # Actualizar el último timestamp guardado
            last_timestamp[node_id] = data_node["timestamp"].max()

            # Guardar datos en formato .mat
            mat_data = {
                "timestamp": data_node["timestamp"].values,
                "temperature": data_node["temperature"].values,
                "humidity": data_node["humidity"].values,
                "pressure": data_node["pressure"].values,
            }
            mat_filename = os.path.join(MAT_DIR, f"nodo_{node_id}.mat")
            sio.savemat(mat_filename, mat_data)
            print(f"✅ Datos actualizados en {mat_filename}")

            # Crear y guardar gráficos individuales
            for metric, color, ylabel in zip(["temperature", "humidity", "pressure"], ['b', 'g', 'r'],
                                             ["Temperatura (°C)", "Humedad (%)", "Presión (hPa)"]):
                plt.figure(figsize=(10, 5))
                plt.plot(data_node["timestamp"], data_node[metric], f'{color}o-', label=ylabel)
                plt.xlabel("Tiempo")
                plt.ylabel(ylabel)
                plt.title(f"{ylabel} del Nodo {node_id}")
                plt.xticks(rotation=45)
                plt.legend()
                plt.grid(True)
                
                # Guardar la gráfica en la carpeta del nodo
                plot_filename = os.path.join(nodo_dir, f"{metric}.png")
                plt.savefig(plot_filename)
                plt.close()
                print(f"📷 Gráfica guardada: {plot_filename}")

    except Exception as e:
        print(f"⚠️ Error en la actualización de gráficas: {e}")

    time.sleep(5)  # Esperar 5 segundos antes de volver a leer el archivo

