#include <WiFi.h>
#include <esp_now.h>
#include <HardwareSerial.h>


#define TX_PIN 6  // (TX)
#define RX_PIN 7  // (RX)
// UART1 (para los pines)
// HardwareSerial SerialUART(1); 

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
  // Serial.print("HOLA");
  struct_message datos_recibidos;
  memcpy(&datos_recibidos, incomingData, sizeof(datos_recibidos));
  char buffer[200];
  memset(buffer, 0, sizeof(buffer));
  // Serial.print("MAC: ");
  // for (int i = 0; i < 6; i++) {
  //     Serial.printf("%02X", info->src_addr[i]);
  //     // sprintf(buffer + strlen(buffer))
  //     if (i < 5) Serial.print(":");
  // }
  // Serial.println();
  // Serial.print("T: ");
  // Serial.println(datos_recibidos.temperatura);
  // Serial.print("H: ");
  // Serial.println(datos_recibidos.humedad);
  // Serial.print("p: ");
  // Serial.println(datos_recibidos.presion); 
  // Serial.print("EXT: ");
  // Serial.println(datos_recibidos.exterior);
  sprintf(buffer, "%02X:%02X:%02X:%02X:%02X:%02X,%.2f,%.2f%,%.2f,%d", 
        info->src_addr[0],
        info->src_addr[1],
        info->src_addr[2],
        info->src_addr[3],
        info->src_addr[4],
        info->src_addr[5],
        datos_recibidos.temperatura, 
        datos_recibidos.humedad, 
        datos_recibidos.presion, 
        datos_recibidos.exterior);
  Serial.println(buffer);
}
void setup() {
  // Serial.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
  Serial.begin(115200);
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error al inicializar ESP-NOW");
  }
  // Recepción de medidas
  esp_now_register_recv_cb(receiveDATA);
  // Emisión de mensajes
  esp_now_peer_info_t peerInfo;
  memcpy(peerInfo.peer_addr, macDestino, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("⚠ Error al agregar peer de Broadcast");
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
  // Serial.print("Estado del envío: ");
  // Serial.println(result == ESP_OK ? "✔ Éxito" : "❌ Falló");
  delay(100);
}