#!/bin/bash

echo "🛑 Deteniendo el sistema y archivando datos..."

# Definir rutas de los scripts y archivos
BASE_DIR=$(dirname "$(realpath "$0")")
BUFFER_SCRIPT="$BASE_DIR/vaciar_buffer.py"
GRAFICADOR_SCRIPT="$BASE_DIR/graficar_pendientes.py"
CSV_FILE="$BASE_DIR/sensor_data.csv"

# **Vaciar el buffer antes de archivar**
echo "📤 Procesando datos pendientes en buffer..."
python "$BUFFER_SCRIPT"

# **Graficar los datos pendientes**
echo "📊 Generando gráficas pendientes..."
python "$GRAFICADOR_SCRIPT"

echo "✅ Graficado finalizado."

# **Archivar las gráficas**
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
