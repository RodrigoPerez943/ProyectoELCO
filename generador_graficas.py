import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.io
import os

# Cargar el archivo CSV
file_path = "E:\ETSIT\TEL\Cuarto\ELCO\PROYECTO\sensor_data.csv"  # Reemplaza con la ruta de tu archivo
df = pd.read_csv(file_path)

# Convertir el timestamp a un formato legible si es necesario
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

#Crear carpetas para guardar archivos
output_folder_mat = "mat_files"
output_folder_png = "graficas"
os.makedirs(output_folder_mat, exist_ok=True)
os.makedirs(output_folder_png, exist_ok=True)

# Obtener lista de node_id únicos
nodes = df["node_id"].unique()

# Generar gráficas para cada node_id
for node in nodes:
    node_df = df[df["node_id"] == node]

    plt.figure(figsize=(10, 5))

    # Gráfica de Temperatura
    plt.subplot(3, 1, 1)
    plt.plot(node_df["timestamp"], node_df["temperature"], marker="o", linestyle="-", label="Temperatura")
    plt.xlabel("Tiempo")
    plt.ylabel("Temperatura (°C)")
    plt.title(f"Temperatura del Nodo {node}")
    plt.legend()
    plt.grid()

    # Gráfica de Humedad
    plt.subplot(3, 1, 2)
    plt.plot(node_df["timestamp"], node_df["humidity"], marker="o", linestyle="-", label="Humedad", color="g")
    plt.xlabel("Tiempo")
    plt.ylabel("Humedad (%)")
    plt.title(f"Humedad del Nodo {node}")
    plt.legend()
    plt.grid()

    # Gráfica de Presión
    plt.subplot(3, 1, 3)
    plt.plot(node_df["timestamp"], node_df["pressure"], marker="o", linestyle="-", label="Presión", color="r")
    plt.xlabel("Tiempo")
    plt.ylabel("Presión (hPa)")
    plt.title(f"Presión del Nodo {node}")
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()

    # Guardar datos en un archivo .mat para MATLAB
    mat_data = {
        "temperature": node_df["temperature"].values,
        "humidity": node_df["humidity"].values,
        "pressure": node_df["pressure"].values,
        "timestamp": node_df["timestamp"].astype("int64").values,
    }
    mat_path = os.path.join(output_folder_mat, f"data_node_{node}.mat")
    scipy.io.savemat(mat_path, mat_data)

    # Guardar la imagen en la carpeta
    image_path = os.path.join(output_folder_png, f"grafica_nodo_{node}.png")
    plt.tight_layout()
    plt.draw()  # Renderiza la figura en segundo plano
    plt.pause(0.1)  # Espera un momento antes de guardar
    plt.savefig(image_path, dpi=300)
    plt.close()

    print(f"Gráfica guardada: {image_path}")