#include <Wire.h>
#include <esp_now.h>
#include <WiFi.h>
#include "sensor_data.pb.h"  // Archivo generado por nanopb (actualiza el .proto para incluir 'pressure' si es necesario)
#include <pb_encode.h>
#include <Adafruit_BMP280.h> // Librería para el sensor BMP280

// Direcciones I2C de los sensores
#define AHT20_ADDR 0x38      // Dirección del AHT20 (puede variar según el módulo)
#define BMP280_ADDR 0x76     // Dirección del BMP280 (algunos módulos usan 0x77)

// Tamaño del buffer para el mensaje Protocol Buffers
const int MESSAGE_BUFFER_SIZE = 128;
uint8_t message_buffer[MESSAGE_BUFFER_SIZE];

// Dirección MAC del HUB central (reemplaza con la dirección real)
uint8_t hubAddress[] = {0x24, 0x6F, 0x28, 0xAA, 0xBB, 0xCC};

// Instancia para el sensor BMP280
Adafruit_BMP280 bmp;

// Callback que se ejecuta cuando se envía un mensaje vía ESP-NOW
void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Estado del envío: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Éxito" : "Fallo");
}

/*
  Función para leer datos del sensor AHT20 (temperatura y humedad)

  Procedimiento:
    1. Envía el comando de medición: [0xAC, 0x33, 0x00]
    2. Espera ~80ms para que la medición se complete.
    3. Lee 6 bytes de respuesta.
    4. Extrae los 20 bits de humedad y 20 bits de temperatura, y los convierte:
         - Humedad (%)    = (rawHumidity / 2^20) * 100
         - Temperatura (°C) = (rawTemperature / 2^20) * 200 - 50
*/
bool readAHT20(float &temperature, float &humidity) {
  // Inicia la medición enviando el comando
  Wire.beginTransmission(AHT20_ADDR);
  Wire.write(0xAC);
  Wire.write(0x33);
  Wire.write(0x00);
  if (Wire.endTransmission() != 0) {
    Serial.println("Error al enviar comando al AHT20");
    return false;
  }
  
  delay(80); // Tiempo para completar la medición (~80ms)
  
  // Solicita 6 bytes de datos
  Wire.requestFrom(AHT20_ADDR, 6);
  if (Wire.available() < 6) {
    Serial.println("Error al leer datos del AHT20");
    return false;
  }
  
  uint8_t data[6];
  for (int i = 0; i < 6; i++) {
    data[i] = Wire.read();
  }
  
  // Conversión de los datos:
  // Los datos vienen organizados en 6 bytes. Se obtiene:
  //   rawHumidity  = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
  //   rawTemperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
  uint32_t rawHumidity = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | ((uint32_t)data[3] >> 4);
  uint32_t rawTemperature = (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];
  
  humidity   = (rawHumidity / 1048576.0f) * 100.0f;          // 2^20 = 1048576
  temperature = (rawTemperature / 1048576.0f) * 200.0f - 50.0f;
  
  return true;
}

/*
  Función para leer la presión del sensor BMP280.

  Se utiliza la librería Adafruit_BMP280, que se encarga de la lectura y compensación.
  La función readPressure() devuelve la presión en Pascales (Pa).
*/
bool readBMP280(float &pressure) {
  pressure = bmp.readPressure();
  if (pressure == 0) {
    Serial.println("Error al leer BMP280");
    return false;
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();  // Inicializa I2C
  Serial.println("Nodo sensor - ESP32-C3 con AHT20 y BMP280");

  // Inicializa el BMP280
  if (!bmp.begin(BMP280_ADDR)) {
    Serial.println("Error al inicializar BMP280");
    // Puedes optar por detener la ejecución o continuar sin BMP280
  }

  // Configura el WiFi en modo STA para usar ESP-NOW
  WiFi.mode(WIFI_STA);
  
  // Inicializa ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error al inicializar ESP-NOW");
    return;
  }
  
  // Registra la función callback para el envío de datos
  esp_now_register_send_cb(onDataSent);
  
  // Agrega el HUB como peer
  esp_now_peer_info_t peerInfo;
  memcpy(peerInfo.peer_addr, hubAddress, 6);
  peerInfo.channel = 0;      // Canal actual
  peerInfo.encrypt = false;  // Sin encriptación
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Error al agregar el peer");
    return;
  }
}

void loop() {
  float temperature, humidity, pressure;
  bool okAHT20 = readAHT20(temperature, humidity);
  bool okBMP   = readBMP280(pressure);
  
  if (okAHT20 && okBMP) {
    Serial.print("Temperatura (AHT20): ");
    Serial.print(temperature);
    Serial.print(" °C, Humedad: ");
    Serial.print(humidity);
    Serial.print(" %, Presión (BMP280): ");
    Serial.print(pressure);
    Serial.println(" Pa");

    // Prepara el mensaje con los datos del sensor para Protocol Buffers
    SensorData sensor_data = SensorData_init_zero; // Inicializa la estructura a cero
    sensor_data.temperature = temperature;
    sensor_data.humidity    = humidity;
    sensor_data.pressure    = pressure; // Asegúrate de tener este campo en tu .proto
    sensor_data.timestamp   = (uint32_t)millis(); // Se utiliza millis() como ejemplo de timestamp

    // Asigna el identificador del nodo
    strncpy(sensor_data.node_id, "NODE_01", sizeof(sensor_data.node_id));

    // Crea el stream de salida para nanopb
    pb_ostream_t stream = pb_ostream_from_buffer(message_buffer, MESSAGE_BUFFER_SIZE);
    if (!pb_encode(&stream, SensorData_fields, &sensor_data)) {
      Serial.print("Error al codificar: ");
      Serial.println(PB_GET_ERROR(&stream));
    } else {
      size_t message_length = stream.bytes_written;
      // Envía el mensaje codificado vía ESP-NOW al HUB
      esp_err_t result = esp_now_send(hubAddress, message_buffer, message_length);
      if (result == ESP_OK) {
        Serial.println("Mensaje enviado correctamente");
      } else {
        Serial.print("Error al enviar el mensaje: ");
        Serial.println(result);
      }
    }
  } else {
    Serial.println("Error al leer uno o más sensores");
  }
  
  // Espera un minuto antes de la siguiente medición (ajusta el delay según tus necesidades)
  delay(60000);
}
