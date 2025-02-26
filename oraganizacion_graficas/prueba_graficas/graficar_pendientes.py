import os
import pandas as pd
import matplotlib.pyplot as plt

# Directorios y archivos clave
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
PNG_DIR = os.path.join(BASE_DIR, "graficas_png")

# Crear carpeta de imágenes si no existe
os.makedirs(PNG_DIR, exist_ok=True)

def graficar_pendientes():
    """ Genera gráficas con los datos pendientes antes de cerrar el sistema """
    if not os.path.exists(CSV_FILE):
        print("⚠️ No hay datos en el CSV para graficar.")
        return

    try:
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            print("⚠️ No hay datos en el CSV.")
            return

        # Graficar temperatura
        plt.figure(figsize=(8, 4))
        for node_id in df["node_id"].unique():
            data_node = df[df["node_id"] == node_id]
            plt.plot(data_node["timestamp"], data_node["temperature"], marker="o", label=f"Nodo {node_id}")

        plt.xlabel("Tiempo")
        plt.ylabel("Temperatura (°C)")
        plt.title("Temperatura de los nodos")
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(PNG_DIR, "temperatura_final.png"))
        plt.close()
        print(f"📷 Gráfica de temperatura actualizada en {PNG_DIR}/temperatura_final.png")

        # Graficar humedad
        plt.figure(figsize=(8, 4))
        for node_id in df["node_id"].unique():
            data_node = df[df["node_id"] == node_id]
            plt.plot(data_node["timestamp"], data_node["humidity"], marker="s", label=f"Nodo {node_id}")

        plt.xlabel("Tiempo")
        plt.ylabel("Humedad (%)")
        plt.title("Humedad de los nodos")
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(PNG_DIR, "humedad_final.png"))
        plt.close()
        print(f"📷 Gráfica de humedad actualizada en {PNG_DIR}/humedad_final.png")

    except Exception as e:
        print(f"⚠️ Error al graficar datos pendientes: {e}")

if __name__ == "__main__":
    graficar_pendientes()
