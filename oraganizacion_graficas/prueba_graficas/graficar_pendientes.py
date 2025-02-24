import os
import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "sensor_data.csv"
PNG_DIR = "graficas_png"

# Crear carpeta si no existe
os.makedirs(PNG_DIR, exist_ok=True)

print("📊 Graficando datos pendientes...")

# Leer el CSV
df = pd.read_csv(CSV_FILE)

if df.empty:
    print("⚠️ No hay datos pendientes en el CSV.")
    exit(0)

# Obtener nodos únicos
nodos = df["node_id"].unique()

for node_id in nodos:
    data_node = df[df["node_id"] == node_id]

    # Diccionario para las gráficas
    medidas = {"temperature": "Temperatura (°C)", "humidity": "Humedad (%)", "pressure": "Presión (hPa)"}

    for key, label in medidas.items():
        plt.figure(figsize=(10, 5))
        plt.plot(data_node["timestamp"], data_node[key], 'bo-', linestyle="dashed", label=f"{label} (Actualizado)")

        plt.xlabel("Tiempo")
        plt.ylabel(label)
        plt.title(f"{label} del Nodo {node_id}")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True)

        # Guardar la gráfica
        file_path = os.path.join(PNG_DIR, f"nodo_{node_id}/{key}.png")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        plt.savefig(file_path)
        plt.close()

        print(f"✅ Gráfica de {label} guardada en {file_path}")

print("📊 Todas las gráficas pendientes han sido generadas correctamente.")
