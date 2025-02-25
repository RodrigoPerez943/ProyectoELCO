#!/bin/bash

echo "🛑 Deteniendo el sistema y archivando datos..."

# Definir rutas de los scripts y archivos
BASE_DIR=$(dirname "$(realpath "$0")")
RECOLECTOR_SCRIPT="$BASE_DIR/recolector_uart.py"
GRAFICADOR_SCRIPT="$BASE_DIR/actualizar_graficas.py"
BUFFER_FILE="$BASE_DIR/buffer_uart.json"
CSV_FILE="$BASE_DIR/sensor_data.csv"

# **Enviar señal de detención a escuchar_uart.py**
echo "📢 Enviando señal de detención a escuchar_uart.py..."
pkill -f "escuchar_uart.py"

# **Esperar a que se procese la cola antes de cerrar**
echo "⏳ Esperando a que escuchar_uart.py termine de procesar la cola..."
sleep 2  # Da tiempo a que termine de vaciar la cola en memoria

# **Procesar los datos restantes en el buffer**
if [ -s "$BUFFER_FILE" ]; then
    echo "📂 Procesando mediciones almacenadas en el buffer..."
    python "$RECOLECTOR_SCRIPT"
else
    echo "✅ Cola de memoria vacía."
fi

# **Esperar a que las gráficas se actualicen**
echo "📊 Esperando a que las gráficas se actualicen..."
python "$GRAFICADOR_SCRIPT"

# **Forzar cierre de `actualizar_graficas.py` si sigue corriendo**
if pgrep -f "actualizar_graficas.py" > /dev/null; then
    echo "⚠️ El proceso de graficado sigue activo, forzando su cierre..."
    pkill -f "actualizar_graficas.py"
fi

echo "✅ Graficador finalizado con éxito."

# **Mover archivos a backup**
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVO_DIR="$BASE_DIR/backup_$FECHA"
mkdir -p "$ARCHIVO_DIR"

if [ -d "$BASE_DIR/graficas_png" ]; then
    mv "$BASE_DIR/graficas_png" "$ARCHIVO_DIR/"
    echo "📁 Carpetas de imágenes PNG movidas a backup."
fi

if [ -d "$BASE_DIR/graficas_mat" ]; then
    mv "$BASE_DIR/graficas_mat" "$ARCHIVO_DIR/"
    echo "📁 Carpetas de imágenes MAT movidas a backup."
fi

echo "✅ Archivos de gráficas movidos a: $ARCHIVO_DIR"

# **Eliminar el CSV después de archivar**
if [ -f "$CSV_FILE" ]; then
    rm -f "$CSV_FILE"
    echo "🗑️ Archivo CSV eliminado correctamente."
else
    echo "⚠️ No se encontró sensor_data.csv."
fi

echo "✅ Sistema detenido y datos archivados."
exit 0
