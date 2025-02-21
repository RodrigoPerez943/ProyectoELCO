import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_FILE = "sensor_data.csv"

print("📊 Graficando datos pendientes...")

try:
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            print("✅ No hay datos pendientes para graficar.")
        else:
            nodos = df["node_id"].unique()

            for nodo in nodos:
                datos_nodo = df[df["node_id"] == nodo]

                plt.figure(figsize=(10, 5))
                plt.plot(datos_nodo["timestamp"], datos_nodo["temperature"], label="Temperatura")
                plt.plot(datos_nodo["timestamp"], datos_nodo["humidity"], label="Humedad")
                plt.plot(datos_nodo["timestamp"], datos_nodo["pressure"], label="Presión")
                plt.xlabel("Tiempo")
                plt.ylabel("Valores")
                plt.title(f"Datos del Nodo {nodo}")
                plt.legend()
                plt.xticks(rotation=45)
                plt.grid()
                plt.tight_layout()
                plt.savefig(f"graficas_png/nodo_{nodo}.png")
                plt.close()

                print(f"✅ Gráfica actualizada para nodo {nodo}.")

            print("✅ Todas las gráficas han sido actualizadas correctamente.")

    else:
        print("⚠️ No se encontró el archivo CSV.")

except KeyboardInterrupt:
    print("\n🛑 Interrupción detectada. Cerrando el proceso de graficado.")
    plt.close('all')
