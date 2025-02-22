#!/bin/bash

echo "🛑 Deteniendo el sistema y archivando datos..."

# Definir rutas
BASE_DIR=$(dirname "$(realpath "$0")")
CSV_FILE="$BASE_DIR/sensor_data.csv"
BUFFER_FILE="$BASE_DIR/buffer_uart.json"

# **Indicar a `escuchar_uart.py` que debe detenerse**
echo "⏳ Enviando señal de detención a escuchar_uart.py..."
touch "$BASE_DIR/stop_signal.flag"

# **Esperar a que la cola en memoria se vacíe**
echo "📤 Procesando mediciones almacenadas en la cola..."
python "$BASE_DIR/vaciar_cola.py"

# **Esperar hasta que las gráficas se actualicen**
echo "📊 Generando gráficas pendientes..."
python "$BASE_DIR/graficar_pendientes.py"

# **Crear carpeta de backup**
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="$BASE_DIR/backup_$FECHA"
mkdir -p "$BACKUP_DIR"

# **Mover archivos a backup**
echo "📂 Archivando datos..."
if [ -d "$BASE_DIR/graficas_png" ]; then
    mv "$BASE_DIR/graficas_png" "$BACKUP_DIR/"
    echo "✅ Gráficas PNG archivadas."
fi

if [ -d "$BASE_DIR/graficas_mat" ]; then
    mv "$BASE_DIR/graficas_mat" "$BACKUP_DIR/"
    echo "✅ Datos MAT archivados."
fi

# **Eliminar el CSV después de archivar los datos**
if [ -f "$CSV_FILE" ]; then
    rm -f "$CSV_FILE"
    echo "🗑️ Archivo CSV eliminado correctamente."
else
    echo "⚠️ No se encontró sensor_data.csv."
fi

# **Eliminar buffer si existe**
if [ -f "$BUFFER_FILE" ]; then
    rm -f "$BUFFER_FILE"
    echo "🗑️ Buffer UART eliminado."
else
    echo "⚠️ No se encontró buffer_uart.json."
fi

# **Eliminar la señal de detención**
rm -f "$BASE_DIR/stop_signal.flag"

echo "✅ Sistema detenido y datos archivados correctamente."
exit 0
