import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.io as sio
import time
import matplotlib.dates as mdates

# **Directorios base**
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
MAT_DIR = os.path.join(BASE_DIR, "graficas_mat")
PNG_DIR = os.path.join(BASE_DIR, "graficas_png")

# **Crear carpetas base si no existen**
os.makedirs(MAT_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

print("📊 Monitoreando `sensor_data.csv` para actualizar gráficas...")

while True:
    try:
        # **Verificar si el archivo `sensor_data.csv` existe y tiene datos**
        if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
            print("⚠️ No hay datos en `sensor_data.csv`. Esperando...")
            time.sleep(5)
            continue

        df = pd.read_csv(CSV_FILE)

        if df.empty:
            print("⚠️ `sensor_data.csv` está vacío. Esperando nuevas mediciones...")
            time.sleep(5)
            continue

        # **Convertir timestamps correctamente**
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", infer_datetime_format=True)
        df = df.dropna(subset=["timestamp"])

        # **Obtener nodos únicos**
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]

            # **Verificar si hay datos**
            if data_node.empty:
                print(f"⚠️ No hay datos para el Nodo {node_id}, saltando...")
                continue

            print(f"📊 Datos disponibles para Nodo {node_id}:")
            print(data_node[["timestamp", "temperature", "humidity", "pressure"]])

            # **Definir ruta de almacenamiento**
            node_dir = os.path.join(MAT_DIR, f"nodo_{node_id}")
            os.makedirs(node_dir, exist_ok=True)

            png_dir = os.path.join(PNG_DIR, f"nodo_{node_id}")
            os.makedirs(png_dir, exist_ok=True)

            mat_filename = os.path.join(node_dir, f"nodo_{node_id}.mat")

            # **Guardar datos en formato `.mat`**
            mat_data = {
                "timestamp": data_node["timestamp"].dt.strftime("%H:%M:%S.%f").values,
                "temperature": data_node["temperature"].values,
                "humidity": data_node["humidity"].values,
                "pressure": data_node["pressure"].values,
            }
            sio.savemat(mat_filename, mat_data)
            print(f"✅ Datos actualizados en {mat_filename}")

            # **Graficar datos acumulados**
            medidas = {
                "temperature": ("Temperatura", "°C", 'bo-', "temperatura.png"),
                "humidity": ("Humedad", "%", 'go-', "humedad.png"),
                "pressure": ("Presión", "hPa", 'ro-', "presion.png"),
            }

            for key, (titulo, unidad, color, archivo) in medidas.items():
                archivo_png = os.path.join(png_dir, archivo)

                # **Ordenar datos por timestamp**
                ordenado = data_node[["timestamp", key]].drop_duplicates().sort_values("timestamp")

                fig, ax = plt.subplots(figsize=(10, 5))

                # **Fijar rango desde las 00:00 hasta las 23:59**
                start_of_day = pd.Timestamp.today().replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = pd.Timestamp.today().replace(hour=23, minute=59, second=59, microsecond=999999)
                ax.set_xlim(start_of_day, end_of_day)

                # **Etiquetas cada hora y subdivisiones cada 15 minutos**
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # ✅ Cada hora
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))  # ✅ Cada 15 minutos
                plt.xticks(rotation=45)

                # **Graficar**
                plt.plot(ordenado["timestamp"], ordenado[key], color, marker="o", label=f"{titulo} del Nodo {node_id}")

                plt.xlabel("Hora del día (HH:MM)")
                plt.ylabel(f"{titulo} ({unidad})")
                plt.title(f"{titulo} del Nodo {node_id}")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()
                plt.savefig(archivo_png)
                plt.close()
                print(f"📷 Gráfica de {titulo} actualizada en {archivo_png}")

    except Exception as e:
        print(f"⚠️ Error en la actualización de gráficas: {e}")

    time.sleep(5)
