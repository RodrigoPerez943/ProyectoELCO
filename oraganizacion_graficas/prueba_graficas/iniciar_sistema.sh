#!/bin/bash

echo "🔄 Iniciando sistema de adquisición y graficado en la Raspberry Pi..."

# Definir la ruta base del proyecto
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📂 Directorio base: $BASE_DIR"

# Definir rutas de los scripts
UART_SCRIPT="$BASE_DIR/recolector_uart.py"
GRAFICAS_SCRIPT="$BASE_DIR/actualizar_graficas.py"
ESCUCHAR_SCRIPT="$BASE_DIR/escuchar_uart.py"
DASHBOARD_SCRIPT="$BASE_DIR/dashboard.py"
DATABASE_SCRIPT="$BASE_DIR/database.py"
# Verificar que los archivos existen antes de ejecutarlos
if [ ! -f "$ESCUCHAR_SCRIPT" ]; then
    echo "❌ Error: No se encontró $ESCUCHAR_SCRIPT"
    exit 1
fi

if [ ! -f "$UART_SCRIPT" ]; then
    echo "❌ Error: No se encontró $UART_SCRIPT"
    exit 1
fi

if [ ! -f "$GRAFICAS_SCRIPT" ]; then
    echo "❌ Error: No se encontró $GRAFICAS_SCRIPT"
    exit 1
fi

# Iniciar scripts en segundo plano
python "$DATABASE_SCRIPT" &
echo "📡 Iniciando escucha de datos UART..."
python "$ESCUCHAR_SCRIPT" &



sleep 5

echo "📊 Iniciando actualización de gráficas..."
python "$GRAFICAS_SCRIPT" &

python "$DASHBOARD_SCRIPT" &

# Evitar que el script termine inmediatamente
wait
