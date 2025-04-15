import smtplib
from email.mime.text import MIMEText
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOMBRES_FILE = os.path.join(BASE_DIR, "sensor_nombres.json")
ALERTAS_FILE = os.path.join(BASE_DIR, "alertas_config.json")
EMAIL_CONFIG_FILE = os.path.join(BASE_DIR, "email_config.json")

# Función para cargar configuración del email
def cargar_config_email():
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# Función para enviar alerta
def enviar_alerta_email(nombre_sensor, temperatura, limite, tipo_alerta):

    config = cargar_config_email()
    EMAIL_SENDER = config.get("sender")
    EMAIL_PASSWORD = config.get("password")
    EMAIL_RECIPIENT = config.get("recipient")
    SMTP_SERVER = config.get("smtp_server", "smtp.gmail.com")
    SMTP_PORT = config.get("smtp_port", 587)

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("⚠️ Configuración de correo incompleta. No se puede enviar la alerta.")
        return

    asunto = f"🚨 Alerta de temperatura: {nombre_sensor}"
    mensaje = f"""Se ha detectado una temperatura {tipo_alerta} en el sensor: {nombre_sensor}

Temperatura actual: {temperatura}°C
Límite de temperatura {tipo_alerta}: {limite}°C

Por favor, toma medidas adecuadas."""

    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"✅ Alerta enviada para {nombre_sensor}")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")

def verificar_alertas(node_id, temperatura):
    str_id = str(node_id)

    # Cargar nombres
    if os.path.exists(NOMBRES_FILE):
        with open(NOMBRES_FILE, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    # Cargar alertas
    if os.path.exists(ALERTAS_FILE):
        with open(ALERTAS_FILE, "r") as f:
            alertas = json.load(f)
    else:
        alertas = {}

    nombre = nombres.get(str_id, f"Sensor {str_id}")
    alert_config = alertas.get(str_id, {})

    min_temp = alert_config.get("min")
    max_temp = alert_config.get("max")

    print(f"📡 Verificando alertas para nodo {str_id} con temperatura {temperatura}°C")
    print(f"🛑 Límites para {nombre}: min={min_temp}, max={max_temp}")

    if min_temp is not None and temperatura < min_temp:
        print(f"❗ Temperatura {temperatura} < mínima {min_temp}")
        enviar_alerta_email(nombre, temperatura, min_temp, "mínima")

    if max_temp is not None and temperatura > max_temp:
        print(f"❗ Temperatura {temperatura} > máxima {max_temp}")
        enviar_alerta_email(nombre, temperatura, max_temp, "máxima")
