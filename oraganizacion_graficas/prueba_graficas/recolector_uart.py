import os
import csv
import json
from database import insertar_medicion, conectar_db, crear_tabla
from alertas import verificar_alertas
from alertas import enviar_alerta_email
import paho.mqtt.publish as mqtt_publish


# Crear la tabla si no existe
crear_tabla()

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

BUFFER_FILE = os.path.join(BASE_DIR, "buffer_uart.json")
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")
MAC_MAPPING_FILE = os.path.join(BASE_DIR, "mac_mapping.json")
MQTT_CONFIG_FILE = os.path.join(BASE_DIR, "mqtt_config.json")

# 📥 Leer configuración del broker MQTT
if os.path.exists(MQTT_CONFIG_FILE):
    with open(MQTT_CONFIG_FILE, "r") as f:
        config = json.load(f)
        MQTT_BROKER_IP = config.get("ip", "192.168.1.130")
        MQTT_BROKER_PORT = config.get("port", 1883)
else:
    MQTT_BROKER_IP = "192.168.1.130"
    MQTT_BROKER_PORT = 1883

def publicar_mqtt(node_id, temperatura, humedad, presion):
    DISCOVERY_FLAG_FILE = os.path.join(BASE_DIR, "mqtt_discovery_flags.json")
    NOMBRES_FILE = os.path.join(BASE_DIR, "sensor_nombres.json")

    str_node_id = str(node_id)

    # 🧾 Cargar nombre personalizado
    if os.path.exists(NOMBRES_FILE):
        with open(NOMBRES_FILE, "r") as f:
            nombres = json.load(f)
    else:
        nombres = {}

    nombre_sensor = nombres.get(str_node_id, f"Sensor {node_id}")

    # 📤 Publicar valores
    payload = {
        "temperatura": float(temperatura),
        "humedad": float(humedad),
        "presion": float(presion)
    }

    topic_datos = f"sensores/{node_id}/datos"
    mqtt_publish.single(
        topic_datos,
        payload=json.dumps(payload),
        hostname=MQTT_BROKER_IP,
        port=MQTT_BROKER_PORT
    )
    print(f"📡 MQTT enviado a {topic_datos} → {payload}")

    # 🧠 MQTT Discovery
    if os.path.exists(DISCOVERY_FLAG_FILE):
        with open(DISCOVERY_FLAG_FILE, "r") as f:
            discovery_flags = json.load(f)
    else:
        discovery_flags = {}

    if str_node_id not in discovery_flags:
        discovery_prefix = "homeassistant"
        base_topic = f"{discovery_prefix}/sensor"

        sensores = {
            "temperatura": {"unit": "°C", "device_class": "temperature"},
            "humedad": {"unit": "%", "device_class": "humidity"},
            "presion": {"unit": "hPa", "device_class": "pressure"}
        }

        for tipo, meta in sensores.items():
            config_topic = f"{base_topic}/nodo{node_id}_{tipo}/config"
            config_payload = {
                "name": tipo.capitalize(),  # Solo "Temperatura", "Humedad", etc.
                "state_topic": topic_datos,
                "unit_of_measurement": meta["unit"],
                "value_template": f"{{{{ value_json.{tipo} }}}}",
                "unique_id": f"nodo{node_id}_{tipo}",
                "device_class": meta["device_class"],
                "device": {
                    "identifiers": [f"nodo{node_id}"],
                    "name": nombre_sensor,  # Este es el nombre del dispositivo
                    "manufacturer": "Sistema de Sensores UART-MQTT"
                }
            }


            mqtt_publish.single(
                config_topic,
                payload=json.dumps(config_payload),
                hostname=MQTT_BROKER_IP,
                port=MQTT_BROKER_PORT,
                retain=True
            )
            print(f"🧠 Sensor MQTT autodetectado publicado: {config_topic}")

        discovery_flags[str_node_id] = True
        with open(DISCOVERY_FLAG_FILE, "w") as f:
            json.dump(discovery_flags, f, indent=4)


def cargar_mac_mapping():
    if os.path.exists(MAC_MAPPING_FILE):
        with open(MAC_MAPPING_FILE, "r") as file:
            return json.load(file)
    return {}

def guardar_mac_mapping(mac_mapping):
    with open(MAC_MAPPING_FILE, "w") as file:
        json.dump(mac_mapping, file, indent=4)

def obtener_node_id(mac_address, mac_mapping):
    if mac_address in mac_mapping:
        return mac_mapping[mac_address]
    else:
        new_node_id = len(mac_mapping) + 1
        mac_mapping[mac_address] = new_node_id
        guardar_mac_mapping(mac_mapping)

        # Generar posición por defecto
        pos_file = os.path.join(BASE_DIR, "sensor_positions.json")
        if os.path.exists(pos_file):
            with open(pos_file, "r") as f:
                posiciones = json.load(f)
        else:
            posiciones = {}

        if str(new_node_id) not in posiciones:
            x = 5 + (new_node_id - 1) * 10 % 90
            y = 5 + ((new_node_id - 1) * 10 // 90) * 10
            posiciones[str(new_node_id)] = {"x": x, "y": y}
            with open(pos_file, "w") as f:
                json.dump(posiciones, f, indent=4)

        return new_node_id

mac_mapping = cargar_mac_mapping()

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "node_id", "temperature", "humidity", "pressure", "ext"])
    print(f"✅ Archivo CSV creado en: {CSV_FILE}")

def procesar_mediciones():
    """ Procesa las mediciones en el buffer y las guarda en CSV y la base de datos. """
    if not os.path.exists(BUFFER_FILE) or os.path.getsize(BUFFER_FILE) == 0:
        print("⚠️ No hay datos en el buffer para procesar.")
        return

    try:
        with open(BUFFER_FILE, "r") as file:
            mediciones = json.load(file)
    except json.JSONDecodeError:
        print("⚠️ Error al leer el buffer. Posible corrupción de datos.")
        return

    if not mediciones:
        print("⚠️ Buffer vacío, no hay datos para procesar.")
        return

    batch = []

    for medicion in mediciones:
        try:
            timestamp, mac, temperature, humidity, pressure, ext = medicion

            temperature = float(temperature)
            humidity = float(humidity)
            pressure = float(pressure)
            ext = float(ext)

            node_id = obtener_node_id(mac, mac_mapping)

            batch.append([timestamp, node_id, temperature, humidity, pressure, ext])

            # Insertar en la base de datos
            insertar_medicion(timestamp, node_id, temperature, humidity, pressure, ext)

            # 🚨 Verificar alertas tras insertar la medición
            verificar_alertas(node_id, temperature, humidity, pressure)

            publicar_mqtt(node_id, temperature, humidity, pressure)


        except Exception as e:
            mensaje = f"⚠️ Error al procesar una línea del buffer: {e}"
            if 'node_id' in locals():
                mensaje += f" (Nodo {node_id})"
            print(mensaje)

    if batch:
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(batch)         

        print(f"✅ {len(batch)} mediciones procesadas y guardadas en el CSV.")

    with open(BUFFER_FILE, "w") as file:
        json.dump([], file)

if __name__ == "__main__":
    procesar_mediciones()
