#include <WiFi.h>
#include <esp_now.h>
#include <HardwareSerialUART.h>


#define TX_PIN 6  // (TX)
#define RX_PIN 7  // (RX)
// UART1 (para los pines)
HardwareSerial SerialUART(1); 

// Prueba para el master, la mac destino es broadcast
uint8_t macDestino[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// Estructura del mensaje
typedef struct struct_message {
    float temperatura;
    float humedad;
    float presion;
    uint8_t exterior;
} struct_message;

// Configuro lo que pasa cuando se recibe
void receiveDATA(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  // SerialUART.print("HOLA");
  struct_message datos_recibidos;
  memcpy(&datos_recibidos, incomingData, sizeof(datos_recibidos));
  SerialUART.print("MAC: ");
  for (int i = 0; i < 6; i++) {
      SerialUART.printf("%02X", info->src_addr[i]);
      if (i < 5) SerialUART.print(":");
  }
  SerialUART.println();
  SerialUART.print("T: ");
  SerialUART.println(datos_recibidos.temperatura);
  SerialUART.print("H: ");
  SerialUART.println(datos_recibidos.humedad);
  SerialUART.print("p: ");
  SerialUART.println(datos_recibidos.presion); 
  SerialUART.print("EXT: ");
  SerialUART.println(datos_recibidos.exterior);
}
void setup() {
  SerialUART.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  if (esp_now_init() != ESP_OK) {
    SerialUART.println("Error al inicializar ESP-NOW");
  }
  // Recepción de medidas
  esp_now_register_recv_cb(receiveDATA);
  // Emisión de mensajes
  esp_now_peer_info_t peerInfo;
  memcpy(peerInfo.peer_addr, macDestino, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    SerialUART.println("⚠ Error al agregar peer de Broadcast");
    return;
  }
}

void loop() {
  uint8_t datos[6];
  String macStr = WiFi.macAddress();
  macStr.toUpperCase(); 
  sscanf(macStr.c_str(), "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
          &datos[0], &datos[1], &datos[2], 
          &datos[3], &datos[4], &datos[5]);
  esp_err_t result = esp_now_send(macDestino, datos, sizeof(datos));
  // SerialUART.print("Estado del envío: ");
  // SerialUART.println(result == ESP_OK ? "✔ Éxito" : "❌ Falló");
  delay(100);
}