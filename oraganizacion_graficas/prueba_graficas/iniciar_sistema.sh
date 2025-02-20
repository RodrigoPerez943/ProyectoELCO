#!/bin/bash

echo "🔄 Iniciando sistema de adquisición y graficado en la Raspberry Pi..."

# Definir rutas de los scripts
UART_SCRIPT="recolector_uart.py"
GRAFICAS_SCRIPT="actualizar_graficas.py"

# Activar el entorno virtual de Python si lo usas (descomentar si es necesario)
# source /home/pi/.venv/bin/activate

# Ejecutar el script de recolección de datos (manteniéndolo en segundo plano)
echo "📡 Iniciando recepción de datos por UART..."
python3 "$UART_SCRIPT" &

# Esperar unos segundos para asegurarse de que el CSV tiene datos antes de graficar
sleep 3

# Ejecutar el script de actualización de gráficas (manteniéndolo en segundo plano)
echo "📊 Iniciando actualización de gráficas..."
python3 "$GRAFICAS_SCRIPT" &

# Esperar a que ambos procesos terminen (evita que el script termine inmediatamente)
wait
