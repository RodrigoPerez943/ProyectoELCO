import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.io
import os
from datetime import datetime
import subprocess

#### IMPORTANTE: pip install pandas matplotlib scipy


def find_sensor_data(filename="sensor_data.csv"):
    """
    Busca el archivo 'sensor_data.csv' en la misma carpeta donde está el script.
    
    Parámetros:
        filename (str): Nombre del archivo a buscar.

    Retorna:
        str: Ruta absoluta del archivo si se encuentra.
        None: Si el archivo no se encuentra.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio del script
    file_path = os.path.join(script_dir, filename)  # Ruta completa del archivo en la misma carpeta
    
    if os.path.exists(file_path):  # Verifica si el archivo existe
        return file_path
    else:
        #Para comodidad
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Obtener la ruta del script
        script_path = os.path.join(script_dir, "generador_csv_prueba.py")
        if os.path.exists(script_path):  # Verificar si el script existe
            subprocess.run(["python", script_path], check=True)  # Ejecutar el script
            return find_sensor_data()


    return None  # Si no lo encuentra, devuelve None



# Cargar el archivo CSV
file_path = find_sensor_data() 
df = pd.read_csv(file_path)

# Convertir el timestamp a un formato legible si es necesario
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # Formato YYYYMMDD_HHMMSS

#Crear carpetas para guardar archivos
script_dir = os.path.dirname(os.path.abspath(__file__))  
output_folder_mat = os.path.join(script_dir, "mat_files")  
output_folder_png = os.path.join(script_dir, "graficas") 
os.makedirs(output_folder_mat, exist_ok=True)
os.makedirs(output_folder_png, exist_ok=True)

# Obtener lista de node_id únicos
nodes = df["node_id"].unique()
# Agrupar de 3 en 3
node_groups = [nodes[i:i+3] for i in range(0, len(nodes), 3)]  

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
    mat_filename = f"data_node_{node}_{current_time}.mat"
    mat_path = os.path.join(output_folder_mat, mat_filename)
    scipy.io.savemat(mat_path, mat_data)

    # Guardar la imagen en la carpeta
    image_filename = f"grafica_nodo_{node}_{current_time}.png"
    image_path = os.path.join(output_folder_png,  image_filename)
    plt.tight_layout()
    plt.draw()  # Renderiza la figura en segundo plano
    plt.pause(0.1)  # Espera un momento antes de guardar
    plt.savefig(image_path, dpi=300)
    plt.close()

    print(f"Gráfica guardada: {image_path}")

# Generar gráficas de temperatura de 3 nodos juntos
for idx, group in enumerate(node_groups):
    plt.figure(figsize=(10, 5))

    for node in group:
        node_df = df[df["node_id"] == node]
        plt.plot(node_df["timestamp"], node_df["temperature"], marker="o", linestyle="-", label=f"Nodo {node}")

    plt.xlabel("Tiempo")
    plt.ylabel("Temperatura (°C)")
    plt.title(f"Temperatura de los nodos {', '.join(map(str, group))}")
    plt.legend()
    plt.grid()
    
    # Guardar la imagen
    image_temp_filename = f"Temperatura_nodos_{idx+1}_{current_time}.png"
    image_temp_path = os.path.join(output_folder_png, image_temp_filename)
    plt.savefig(image_temp_path, dpi=300)
    plt.close()

    print(f"Gráfica de temperatura guardada: {image_path}")

print("Generación de gráficas completada.")