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
for directory in [MAT_DIR, PNG_DIR]:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"📂 Carpeta asegurada: {directory}")
    except Exception as e:
        print(f"❌ Error al crear {directory}: {e}")

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
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", format="%Y-%m-%d %H:%M:%S.%f")
        df = df.dropna(subset=["timestamp"])  # Asegurar que no haya timestamps inválidos

        # **Obtener nodos únicos**
        nodos = df["node_id"].unique()

        for node_id in nodos:
            data_node = df[df["node_id"] == node_id]

            # **Verificar si hay datos**
            if data_node.empty:
                print(f"⚠️ No hay datos para el Nodo {node_id}, saltando...")
                continue

            print(f"📊 Datos disponibles para Nodo {node_id}: {len(data_node)} registros.")

            # **Definir ruta de almacenamiento**
            node_dir = os.path.join(MAT_DIR, f"nodo_{node_id}")
            png_dir = os.path.join(PNG_DIR, f"nodo_{node_id}")

            # **Crear directorios del nodo**
            for directory in [node_dir, png_dir]:
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    print(f"❌ Error al crear {directory}: {e}")

            mat_filename = os.path.join(node_dir, f"nodo_{node_id}.mat")

            # **Guardar datos en formato `.mat`**
            try:
                mat_data = {
                    "timestamp": data_node["timestamp"].astype(str).values,  # Convertir a string
                    "temperature": data_node["temperature"].values,
                    "humidity": data_node["humidity"].values,
                    "pressure": data_node["pressure"].values,
                }
                sio.savemat(mat_filename, mat_data)
                print(f"✅ Datos guardados en {mat_filename}")

            except Exception as e:
                print(f"❌ Error al guardar {mat_filename}: {e}")

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

                if ordenado.empty:
                    print(f"⚠️ No hay datos suficientes para {titulo} en Nodo {node_id}, omitiendo gráfica.")
                    continue

                fig, ax = plt.subplots(figsize=(10, 5))

                # **Formato de tiempo en el eje X**
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))  # Divisiones cada 2 minutos

                plt.xticks(rotation=45)

                # **Graficar**
                plt.plot(ordenado["timestamp"], ordenado[key], color, marker="o", label=f"{titulo} del Nodo {node_id}")

                plt.xlabel("Hora del día (HH:MM)")
                plt.ylabel(f"{titulo} ({unidad})")
                plt.title(f"{titulo} del Nodo {node_id}")
                plt.grid(True)
                plt.legend()
                plt.tight_layout()

                # **Guardar la gráfica**
                try:
                    plt.savefig(archivo_png)
                    print(f"📷 Gráfica de {titulo} guardada en {archivo_png}")
                except Exception as e:
                    print(f"❌ Error al guardar la gráfica {archivo_png}: {e}")

                plt.close()

    except Exception as e:
        print(f"⚠️ Error en la actualización de gráficas: {e}")

    time.sleep(5)  # Esperar 5 segundos antes de volver a leer el archivo
