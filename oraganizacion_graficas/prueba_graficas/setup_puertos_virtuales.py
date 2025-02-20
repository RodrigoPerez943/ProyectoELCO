import subprocess
import sys

# Definir los nombres de los puertos virtuales
PUERTO_SIMULADOR = "COM10"
PUERTO_RECOLECTOR = "COM11"

def verificar_com0com():
    """ Verifica si com0com está instalado en Windows. """
    try:
        resultado = subprocess.run(["com0com", "--version"], capture_output=True, text=True)
        if "com0com" in resultado.stdout.lower():
            print("✅ com0com está instalado.")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ com0com no está instalado. Descárgalo desde https://sourceforge.net/projects/com0com/")
    return False

def crear_puertos_virtuales():
    """ Crea los puertos virtuales en com0com si no existen. """
    print("🔧 Creando puertos virtuales en com0com...")

    # Comando para agregar los puertos en com0com
    comando = f'cmd /c "com0com --install -p {PUERTO_SIMULADOR} -p {PUERTO_RECOLECTOR}"'
    
    try:
        subprocess.run(comando, shell=True, check=True)
        print(f"✅ Puertos virtuales creados correctamente: {PUERTO_SIMULADOR} ↔ {PUERTO_RECOLECTOR}")
    except subprocess.CalledProcessError:
        print("❌ Error al crear los puertos virtuales.")
        sys.exit(1)

if __name__ == "__main__":
    if verificar_com0com():
        crear_puertos_virtuales()
