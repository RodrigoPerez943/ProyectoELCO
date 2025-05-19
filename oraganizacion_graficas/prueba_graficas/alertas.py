import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from generar_resumen_graficas import generar_resumen_graficas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOMBRES_FILE = os.path.join(BASE_DIR, "sensor_nombres.json")
ALERTAS_FILE = os.path.join(BASE_DIR, "alertas_config.json")
EMAIL_CONFIG_FILE = os.path.join(BASE_DIR, "email_config.json")
INTERVALO_FILE = os.path.join(BASE_DIR, "intervalo_config.json")

# ───────────────────────────────────────────────────────────────
# Email resumen
# ───────────────────────────────────────────────────────────────

def cargar_config_email():
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def enviar_resumen_email(imagenes):
    config = cargar_config_email()

    sender = config.get("sender")
    password = config.get("password")
    recipient = config.get("recipient")
    smtp_server = config.get("smtp_server", "smtp.gmail.com")
    smtp_port = config.get("smtp_port", 587)

    if not all([sender, password, recipient, smtp_server]):
        print("⚠️ Configuración de correo incompleta. No se puede enviar resumen.")
        return False

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = "📊 Resumen de sensores (gráficas individuales)"

    body = (
        "Adjunto se encuentran las gráficas individuales de temperatura, "
        "humedad y presión de los sensores seleccionados.\n\n"
        "Este correo se ha generado automáticamente."
    )
    msg.attach(MIMEText(body, "plain"))

    for img_path in imagenes:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                image = MIMEImage(f.read(), name=os.path.basename(img_path))
                msg.attach(image)
                print(f"📎 Imagen adjunta: {img_path}")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print("✅ Resumen enviado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al enviar resumen: {e}")
        return False

# ───────────────────────────────────────────────────────────────
# Email de alerta puntual por variable
# ───────────────────────────────────────────────────────────────

def enviar_alerta_email(nombre_sensor, valor_actual, limite, tipo_alerta):
    config = cargar_config_email()
    EMAIL_SENDER = config.get("sender")
    EMAIL_PASSWORD = config.get("password")
    EMAIL_RECIPIENT = config.get("recipient")
    SMTP_SERVER = config.get("smtp_server", "smtp.gmail.com")
    SMTP_PORT = config.get("smtp_port", 587)

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("⚠️ Configuración de correo incompleta. No se puede enviar la alerta.")
        return

    if "temperatura" in tipo_alerta:
        unidad = "°C"
    elif "humedad" in tipo_alerta:
        unidad = "%"
    elif "presión" in tipo_alerta:
        unidad = "hPa"
    else:
        unidad = ""

    asunto = f"🚨 Alerta de {tipo_alerta}: {nombre_sensor}"
    mensaje = f"""Se ha detectado una {tipo_alerta} en el sensor: {nombre_sensor}

Valor actual: {valor_actual}{unidad}
Límite {tipo_alerta}: {limite}{unidad}

Por favor, toma las medidas necesarias."""

    msg = MIMEText(mensaje)
    msg["Subject"] = asunto
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"✅ Alerta enviada para {nombre_sensor} ({tipo_alerta})")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")

# ───────────────────────────────────────────────────────────────
# Comprobación de alertas por sensor
# ───────────────────────────────────────────────────────────────

def verificar_alertas(node_id, temperatura, humedad, presion):
    str_id = str(node_id)

    if os.path.exists(NOMBRES_FILE):
        with open(NOMBRES_FILE, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    nombre = nombres.get(str_id, f"Sensor {str_id}")

    # 🔐 Nueva lógica segura para alertas_config.json
    if os.path.exists(ALERTAS_FILE):
        with open(ALERTAS_FILE, "r") as f:
            alertas = json.load(f)
    else:
        alertas = {}

    alert_config = alertas.setdefault(str_id, {})
    estado = alert_config.setdefault("estado", {
        "min_temp": "ok",
        "max_temp": "ok",
        "min_hum": "ok",
        "max_hum": "ok",
        "min_pres": "ok",
        "max_pres": "ok"
    })

    actualizado = False

    def gestionar_alerta(valor, limite, tipo, comparador):
        nonlocal actualizado
        if comparador(valor, limite):
            if estado[tipo] != "alerta":
                enviar_alerta_email(nombre, valor, limite, tipo.replace("_", " de "))
                estado[tipo] = "alerta"
                actualizado = True
        else:
            if estado[tipo] != "ok":
                estado[tipo] = "ok"
                actualizado = True

    if (lim := alert_config.get("min_temp")) is not None:
        gestionar_alerta(temperatura, lim, "min_temp", lambda v, l: v < l)
    if (lim := alert_config.get("max_temp")) is not None:
        gestionar_alerta(temperatura, lim, "max_temp", lambda v, l: v > l)
    if (lim := alert_config.get("min_hum")) is not None:
        gestionar_alerta(humedad, lim, "min_hum", lambda v, l: v < l)
    if (lim := alert_config.get("max_hum")) is not None:
        gestionar_alerta(humedad, lim, "max_hum", lambda v, l: v > l)
    if (lim := alert_config.get("min_pres")) is not None:
        gestionar_alerta(presion, lim, "min_pres", lambda v, l: v < l)
    if (lim := alert_config.get("max_pres")) is not None:
        gestionar_alerta(presion, lim, "max_pres", lambda v, l: v > l)

    if actualizado:
        with open(ALERTAS_FILE, "w") as f:
            json.dump(alertas, f, indent=4)

# ───────────────────────────────────────────────────────────────
# Ejecución automática de resumen periódico
# ───────────────────────────────────────────────────────────────

def obtener_intervalo():
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("intervalo_resumen", 3600)
    return 3600


def ejecutar_resumen_periodico():
    while True:
        config = cargar_config_email()
        if config.get("resumen_activo"):
            print("📬 Resumen activado: generando y enviando...")
            imagenes = generar_resumen_graficas()
            if imagenes:
                enviar_resumen_email(imagenes)
            else:
                print("⚠️ No se generaron imágenes de resumen.")
        else:
            print("📭 Resumen desactivado. Saltando envío.")

        intervalo = obtener_intervalo()
        print(f"⏳ Esperando {intervalo} segundos para el siguiente resumen...")
        time.sleep(intervalo)
