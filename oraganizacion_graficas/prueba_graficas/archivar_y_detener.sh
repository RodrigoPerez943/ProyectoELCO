#!/bin/bash

echo "🛑 Deteniendo el sistema y archivando datos..."

# Directorios y archivos
BASE_DIR=$(dirname "$(realpath "$0")")
RECOLECTOR_SCRIPT="$BASE_DIR/recolector_uart.py"
ESCUCHAR_SCRIPT="$BASE_DIR/escuchar_uart.py"
GRAFICAR_PENDIENTES="$BASE_DIR/graficar_pendientes.py"
BUFFER_FILE="$BASE_DIR/buffer_uart.json"
CSV_FILE="$BASE_DIR/sensor_data.csv"
GRAFICAS_DIR="$BASE_DIR/graficas_png"
BACKUP_DIR="$BASE_DIR/backup_$(date +"%Y-%m-%d_%H-%M-%S")"

# **Enviar señal de detención a `escuchar_uart.py`**
echo "📢 Enviando señal de detención a escuchar_uart.py..."
pkill -f "escuchar_uart.py"

# **Esperar a que `escuchar_uart.py` termine de procesar la cola**
echo "⏳ Esperando a que escuchar_uart.py termine de procesar la cola..."
sleep 3  # Tiempo para asegurar que todas las mediciones se han procesado

# **Procesar cualquier medición pendiente en el buffer**
if [ -s "$BUFFER_FILE" ]; then
    echo "📝 Procesando mediciones almacenadas en el buffer..."
    python "$RECOLECTOR_SCRIPT" --procesar-buffer
else
    echo "✅ Cola de memoria vacía."
fi

# **Esperar a que las gráficas se actualicen**
echo "⏳ Esperando a que las gráficas se actualicen..."
python "$GRAFICAR_PENDIENTES"

# **Mover los archivos a un backup**
echo "📂 Moviendo archivos de gráficas a backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
mv "$GRAFICAS_DIR" "$BACKUP_DIR/"
mv "$BASE_DIR/graficas_mat" "$BACKUP_DIR/"

echo "✅ Archivos de gráficas movidos a backup."

# **Eliminar versiones antiguas de las gráficas**
echo "🗑️ Eliminando versiones antiguas de las gráficas..."

# Recorrer cada carpeta de nodo dentro de graficas_png
for nodo_dir in "$BACKUP_DIR/graficas_png"/nodo_*; do
    if [ -d "$nodo_dir" ]; then  # Verificar si es un directorio válido
        echo "🔍 Procesando $nodo_dir..."
        
        # Para cada tipo de gráfica (temperatura, humedad, presión)
        for tipo in "temperature" "humidity" "pressure"; do
            archivos=("$nodo_dir"/"$tipo"*.png)  # Buscar todas las versiones del gráfico

            # Si hay más de un archivo, eliminar el más antiguo
            if [ "${#archivos[@]}" -gt 1 ]; then
                archivo_a_borrar=$(ls -t "$nodo_dir"/"$tipo"*.png | tail -n 1)  # Seleccionar el más antiguo
                rm -f "$archivo_a_borrar"
                echo "🗑️ Eliminado archivo antiguo: $archivo_a_borrar"
            fi
        done
    fi
done

echo "✅ Se han eliminado las versiones antiguas de las gráficas."

# Eliminar los archivos base generados por `actualizar_graficas.py`
echo "🗑️ Eliminando archivos base generados por actualizar_graficas..."
find "$BACKUP_DIR/graficas_png" -type f -name "*_base.png" -exec rm {} \;

# **Eliminar el CSV solo después de archivar**
if [ -f "$CSV_FILE" ]; then
    rm -f "$CSV_FILE"
    echo "🗑️ Archivo CSV eliminado correctamente."
else
    echo "⚠️ No se encontró sensor_data.csv."
fi

echo "✅ Sistema detenido y datos archivados."
exit 0
