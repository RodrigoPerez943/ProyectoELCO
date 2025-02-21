import os
import time
import serial.tools.list_ports
import subprocess

# Configuración de los puertos virtuales
PUERTO_SIMULADOR = "COM10"
PUERTO_RECOLECTOR = "COM11"

# Ruta de instalación de VSPE
VSPE_EXE = r"C:/Program Files (x86)/Eterlogic.com/VSPE/vspe.exe"  # Ajusta la ruta si es diferente


def verificar_puertos():
    """ Verifica si los puertos COM10 y COM11 ya existen en el sistema. """
    puertos = [port.device for port in serial.tools.list_ports.comports()]
    
    if PUERTO_SIMULADOR in puertos and PUERTO_RECOLECTOR in puertos:
        print(f"✅ Los puertos {PUERTO_SIMULADOR} y {PUERTO_RECOLECTOR} ya están disponibles.")
        return True
    else:
        print(f"❌ Los puertos {PUERTO_SIMULADOR} y {PUERTO_RECOLECTOR} no existen.")
        return False


def crear_puertos_vsper():
    """ Crea los puertos virtuales COM10 ↔ COM11 en VSPE si no existen. """
    if not os.path.exists(VSPE_EXE):
        print("❌ No se encontró VSPE. Asegúrate de que está instalado en C:\\Program Files (x86)\\Eterlogic.com\\VSPE\\")
        return

    print("🔧 Creando puertos virtuales en VSPE...")
    
    # Comando para iniciar VSPE con los puertos preconfigurados
    comando_vsper = f'"{VSPE_EXE}" /create "pair" "{PUERTO_SIMULADOR}" "{PUERTO_RECOLECTOR}"'
    
    try:
        subprocess.run(comando_vsper, shell=True, check=True)
        print(f"✅ Puertos {PUERTO_SIMULADOR} ↔ {PUERTO_RECOLECTOR} creados correctamente en VSPE.")
        
        # Esperar unos segundos para que Windows registre los nuevos puertos
        time.sleep(3)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear los puertos en VSPE: {e}")


if __name__ == "__main__":
    if not verificar_puertos():
        crear_puertos_vsper()

    if verificar_puertos():
        print("✅ Configuración de puertos virtuales completada con éxito.")
    else:
        print("❌ No se pudieron crear los puertos correctamente. Verifica VSPE manualmente.")
