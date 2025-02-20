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
