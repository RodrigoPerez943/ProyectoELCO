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

print("📊 Monitoreando el archivo CSV para actualizar las gráficas...")

# Estado previo del CSV
last_timestamp = {}

while True:
    try:
        # Leer los datos actuales
        df = pd.read_csv(CSV_FILE)
        #print(df["temperature"])
        if df.empty:
            print("⚠️ No hay datos en el archivo CSV. Esperando nuevas mediciones...")
            time.sleep(5)
            continue

        # Obtener nodos únicos
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]

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

            # Crear figura para el nodo
            fig, axes = plt.subplots(3, 1, figsize=(10, 6))

            # Gráfica de temperatura
            axes[0].plot(data_node["timestamp"], data_node["temperature"], 'bo-', label="Temperatura")
            axes[0].set_ylabel("Temperatura (°C)")
            axes[0].set_title(f"Temperatura del Nodo {node_id}")
            axes[0].legend()

            # Gráfica de humedad
            axes[1].plot(data_node["timestamp"], data_node["humidity"], 'go-', label="Humedad")
            axes[1].set_ylabel("Humedad (%)")
            axes[1].set_title(f"Humedad del Nodo {node_id}")
            axes[1].legend()

            # Gráfica de presión
            axes[2].plot(data_node["timestamp"], data_node["pressure"], 'ro-', label="Presión")
            axes[2].set_ylabel("Presión (hPa)")
            axes[2].set_title(f"Presión del Nodo {node_id}")
            axes[2].legend()

            # Configuración final
            for ax in axes:
                ax.set_xlabel("Tiempo")
                ax.grid(True)

            plt.tight_layout()

            # Guardar imagen en PNG
            png_filename = os.path.join(PNG_DIR, f"nodo_{node_id}.png")
            plt.savefig(png_filename)
            print(f"📷 Gráfica actualizada en {png_filename}")

            plt.close()

    except Exception as e:
        print(f"⚠️ Error en la actualización de gráficas: {e}")


    time.sleep(5)  # Esperar 5 segundos antes de volver a leer el archivo

