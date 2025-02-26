import pandas as pd
import matplotlib.pyplot as plt
import os
import scipy.io as sio
import time
import matplotlib.dates as mdates

# **Directorios base**
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")  # Archivo principal con datos de todos los nodos
MAT_DIR = os.path.join(BASE_DIR, "graficas_mat")  # Carpeta para archivos .mat
PNG_DIR = os.path.join(BASE_DIR, "graficas_png")  # Carpeta para imágenes de gráficas

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

        # **Convertir timestamps a formato datetime con microsegundos**
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%H:%M:%S.%f", errors='coerce')
        df = df.dropna(subset=["timestamp"])  # Eliminar filas con timestamps inválidos

        # **Obtener nodos únicos**
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]  # Filtrar datos de este nodo

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

                # **Configurar Matplotlib con ejes de fecha**
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S.%f"))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.xticks(rotation=45)

                # **Graficar**
                plt.plot(ordenado["timestamp"], ordenado[key], color, label=f"{titulo} del Nodo {node_id}")

                plt.xlabel("Tiempo (HH:MM:SS.μs)")
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

    time.sleep(5)  # Esperar antes de volver a graficar
