#!/bin/bash

echo "🚀 Iniciando sistema de monitoreo UART..."

# Definir rutas de los scripts
BASE_DIR=$(dirname "$(realpath "$0")")
ESC_UART_SCRIPT="$BASE_DIR/escuchar_uart.py"
GRAFICADOR_SCRIPT="$BASE_DIR/actualizar_graficas.py"

# **Verificar si el proceso ya está en ejecución**
if pgrep -f "escuchar_uart.py" > /dev/null; then
    echo "⚠️ El proceso escuchar_uart.py ya está corriendo. Deteniéndolo..."
    pkill -f "escuchar_uart.py"
fi

# **Iniciar la escucha de UART**
echo "📡 Iniciando escucha de datos UART..."
python3 "$ESC_UART_SCRIPT" &  # Ejecutar en segundo plano
sleep 2  # Dar tiempo a iniciar correctamente

# **Iniciar el graficador en segundo plano**
echo "📊 Iniciando actualización de gráficas en segundo plano..."
python3 "$GRAFICADOR_SCRIPT" &

echo "✅ Sistema iniciado correctamente."
exit 0
