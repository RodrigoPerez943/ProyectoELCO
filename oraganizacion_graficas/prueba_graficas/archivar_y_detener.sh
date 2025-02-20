#!/bin/bash

echo "🛑 Deteniendo el sistema de adquisición y graficado..."

# Obtener la ruta del directorio donde está este script
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Buscar los procesos en ejecución y detenerlos
PIDS=$(ps aux | grep -E "recolector_uart.py|actualizar_graficas.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "⚠️ No hay procesos en ejecución."
else
    echo "🔹 Procesos encontrados: $PIDS"
    kill -9 $PIDS
    echo "✅ Procesos detenidos correctamente."
fi

# Crear carpeta con la fecha actual para archivar los datos
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVO_DIR="$BASE_DIR/backup_$FECHA"

mkdir -p "$ARCHIVO_DIR"

# Mover carpetas completas en lugar de solo los archivos internos
if [ -d "$BASE_DIR/graficas_png" ]; then
    mv "$BASE_DIR/graficas_png" "$ARCHIVO_DIR/"
    echo "✅ Carpeta 'graficas_png' movida a $ARCHIVO_DIR/"
else
    echo "⚠️ No se encontró la carpeta 'graficas_png'."
fi

if [ -d "$BASE_DIR/graficas_mat" ]; then
    mv "$BASE_DIR/graficas_mat" "$ARCHIVO_DIR/"
    echo "✅ Carpeta 'graficas_mat' movida a $ARCHIVO_DIR/"
else
    echo "⚠️ No se encontró la carpeta 'graficas_mat'."
fi

# Borrar el archivo CSV
CSV_FILE="$BASE_DIR/sensor_data.csv"
if [ -f "$CSV_FILE" ]; then
    rm -f "$CSV_FILE"
    echo "✅ Archivo CSV eliminado."
else
    echo "⚠️ No se encontró sensor_data.csv, no se eliminó nada."
fi

echo "✅ Todas las carpetas y el CSV han sido archivados en $ARCHIVO_DIR."
