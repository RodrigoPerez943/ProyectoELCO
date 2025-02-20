#!/bin/bash

echo "🛑 Deteniendo el sistema de adquisición y graficado..."

# Buscar los procesos en ejecución y detenerlos
PIDS=$(ps aux | grep -E "recolector_uart.py|actualizar_graficas.py" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "⚠️ No hay procesos en ejecución."
else
    echo "🔹 Procesos encontrados: $PIDS"
    kill -9 $PIDS
    echo "✅ Procesos detenidos correctamente."
fi

# Crear carpeta con la fecha actual
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVO_DIR="backup_$FECHA"

mkdir -p "$ARCHIVO_DIR"

# Mover archivos PNG y MAT a la carpeta
if [ -d "graficas_png" ] && [ "$(ls -A graficas_png)" ]; then
    mv graficas_png/* "$ARCHIVO_DIR/"
    echo "✅ Gráficas PNG movidas a $ARCHIVO_DIR/"
else
    echo "⚠️ No hay archivos PNG para mover."
fi

if [ -d "graficas_mat" ] && [ "$(ls -A graficas_mat)" ]; then
    mv graficas_mat/* "$ARCHIVO_DIR/"
    echo "✅ Archivos MAT movidos a $ARCHIVO_DIR/"
else
    echo "⚠️ No hay archivos MAT para mover."
fi

# Borrar el archivo CSV
if [ -f "sensor_data.csv" ]; then
    rm -f sensor_data.csv
    echo "✅ Archivo CSV eliminado."
else
    echo "⚠️ No se encontró sensor_data.csv, no se eliminó nada."
fi

echo "✅ Todos los datos han sido archivados en $ARCHIVO_DIR y el CSV ha sido eliminado."
