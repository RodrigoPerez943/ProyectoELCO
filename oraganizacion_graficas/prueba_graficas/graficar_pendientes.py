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

print("📊 Procesando las gráficas pendientes...")

# Leer el CSV
try:
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        print("⚠️ No hay datos en el archivo CSV.")
        exit()

    # Obtener nodos únicos
    nodos = df["node_id"].unique()

    for node_id in nodos:
        data_node = df[df["node_id"] == node_id]

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

        # Generar tres gráficas por nodo
        node_folder = os.path.join(PNG_DIR, f"nodo_{node_id}")
        os.makedirs(node_folder, exist_ok=True)

        for variable, color in zip(["temperature", "humidity", "pressure"], ['b', 'g', 'r']):
            plt.figure(figsize=(10, 4))
            plt.plot(data_node["timestamp"], data_node[variable], f'{color}o-', label=variable.capitalize())
            plt.xlabel("Tiempo")
            plt.ylabel("Valor")
            plt.title(f"{variable.capitalize()} del Nodo {node_id}")
            plt.legend()
            plt.grid(True)

            # Guardar la gráfica
            filename = os.path.join(node_folder, f"{variable}.png")
            plt.savefig(filename)
            print(f"📷 Gráfica de {variable} guardada en {filename}")

            plt.close()

    print("✅ Todas las gráficas han sido generadas correctamente.")

except Exception as e:
    print(f"⚠️ Error al procesar las gráficas: {e}")

