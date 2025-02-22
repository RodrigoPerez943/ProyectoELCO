import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.io as sio
import time

CSV_FILE = "sensor_data.csv"
MAT_DIR = "graficas_mat"
PNG_DIR = "graficas_png"

# Crear carpetas base si no existen
os.makedirs(MAT_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

print("📊 Monitoreando el archivo CSV para actualizar las gráficas...")

# Estado previo del CSV
last_timestamp = {}

while True:
    try:
        # Leer datos actuales
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            print("⚠️ No hay datos en el archivo CSV. Esperando nuevas mediciones...")
            time.sleep(5)
            continue

        # **Convertir timestamps a formato datetime con microsegundos**
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%H:%M:%S.%f")

        # Obtener nodos únicos
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]

            # **Verificar si hay nuevos datos comparando con el último timestamp registrado**
            if node_id in last_timestamp and last_timestamp[node_id] >= data_node["timestamp"].max():
                continue  # No hay nuevos datos, pasamos al siguiente nodo

            # **Actualizar el último timestamp guardado**
            last_timestamp[node_id] = data_node["timestamp"].max()

            # **Guardar datos en formato .mat**
            mat_data = {
                "timestamp": data_node["timestamp"].astype(str).values,  # Se guardan con microsegundos
                "temperature": data_node["temperature"].values,
                "humidity": data_node["humidity"].values,
                "pressure": data_node["pressure"].values,
            }
            node_dir = os.path.join(MAT_DIR, f"nodo_{node_id}")
            os.makedirs(node_dir, exist_ok=True)
            mat_filename = os.path.join(node_dir, f"nodo_{node_id}.mat")
            sio.savemat(mat_filename, mat_data)
            print(f"✅ Datos actualizados en {mat_filename}")

            # **Crear carpeta para cada nodo en PNG**
            png_dir = os.path.join(PNG_DIR, f"nodo_{node_id}")
            os.makedirs(png_dir, exist_ok=True)

            # **1️⃣ Gráfica de Temperatura**
            plt.figure(figsize=(8, 4))
            plt.plot(data_node["timestamp"], data_node["temperature"], 'bo-', label="Temperatura")
            plt.xlabel("Tiempo (HH:MM:SS.μs)")
            plt.ylabel("Temperatura (°C)")
            plt.title(f"Temperatura del Nodo {node_id}")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(png_dir, "temperatura.png"))
            plt.close()
            print(f"📷 Gráfica de temperatura guardada en {png_dir}/temperatura.png")

            # **2️⃣ Gráfica de Humedad**
            plt.figure(figsize=(8, 4))
            plt.plot(data_node["timestamp"], data_node["humidity"], 'go-', label="Humedad")
            plt.xlabel("Tiempo (HH:MM:SS.μs)")
            plt.ylabel("Humedad (%)")
            plt.title(f"Humedad del Nodo {node_id}")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(png_dir, "humedad.png"))
            plt.close()
            print(f"📷 Gráfica de humedad guardada en {png_dir}/humedad.png")

            # **3️⃣ Gráfica de Presión**
            plt.figure(figsize=(8, 4))
            plt.plot(data_node["timestamp"], data_node["pressure"], 'ro-', label="Presión")
            plt.xlabel("Tiempo (HH:MM:SS.μs)")
            plt.ylabel("Presión (hPa)")
            plt.title(f"Presión del Nodo {node_id}")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(png_dir, "presion.png"))
            plt.close()
            print(f"📷 Gráfica de presión guardada en {png_dir}/presion.png")

    except Exception as e:
        print(f"⚠️ Error en la actualización de gráficas: {e}")

    time.sleep(5)  # Esperar 5 segundos antes de volver a leer el archivo
