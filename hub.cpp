#include <esp_now.h>
#include <WiFi.h>
#include "sensor_data.pb.h"
#include <pb_decode.h>

// Configuración para la comunicación serial con la Raspberry Pi:
// Se usará Serial2: en este ejemplo, se define el pin TX (puedes ajustarlo según tu hardware).
#define UART_TX_PIN 17      // Pin que se conectará al RX de la Raspberry Pi
#define UART_BAUD_RATE 115200

// Callback que se ejecuta al recibir un mensaje vía ESP-NOW
void onDataRecv(const uint8_t *mac_addr, const uint8_t *incomingData, int len) {
  // Imprime la dirección MAC del nodo emisor para depuración
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02X:%02X:%02X:%02X:%02X:%02X", 
           mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
  Serial.printf("Mensaje recibido de: %s\n", macStr);

  // Decodifica el mensaje recibido usando nanopb
  SensorData sensor_data = SensorData_init_zero; // Inicializa la estructura a cero
  pb_istream_t stream = pb_istream_from_buffer(incomingData, len);
  if (!pb_decode(&stream, SensorData_fields, &sensor_data)) {
    Serial.print("Error al decodificar: ");
    Serial.println(PB_GET_ERROR(&stream));
    return;
  }

  // Muestra los datos recibidos en el monitor serie para depuración
  Serial.print("Temperatura: ");
  Serial.print(sensor_data.temperature);
  Serial.print(" °C, Humedad: ");
  Serial.print(sensor_data.humidity);
  Serial.print(" %, Timestamp: ");
  Serial.println(sensor_data.timestamp);

  // Prepara un mensaje de texto (por ejemplo, en formato CSV) para enviar a la Raspberry Pi.
  // Puedes modificar el formato de acuerdo a tus necesidades.
  String output = String(sensor_data.temperature) + "," +
                  String(sensor_data.humidity) + "," +
                  String(sensor_data.timestamp) + "\n";

  // Envía el mensaje por el puerto serial configurado (Serial2)
  Serial2.print(output);
}

void setup() {
  // Inicializa el Serial principal para depuración
  Serial.begin(115200);
  Serial.println("Hub ESP32: Recibiendo datos via ESP-NOW y enviando a la Raspberry Pi");

  // Inicializa el puerto serial secundario para la comunicación con la Raspberry Pi.
  // En este ejemplo, se usa Serial2. Si no necesitas recibir datos, puedes omitir el pin RX (se usa -1).
  Serial2.begin(UART_BAUD_RATE, SERIAL_8N1, -1, UART_TX_PIN);

  // Configura el WiFi en modo STA (estación) para usar ESP-NOW
  WiFi.mode(WIFI_STA);
  
  // Inicializa ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error al inicializar ESP-NOW");
    return;
  }
  
  // Registra el callback de recepción de datos
  esp_now_register_recv_cb(onDataRecv);
}

void loop() {
  // El hub permanece en espera de recibir mensajes ESP-NOW.
  // No se requiere acción en el loop, por lo que se puede dejar un delay breve.
  delay(100);
}
