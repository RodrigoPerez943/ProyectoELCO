#include <WiFi.h>
#include <esp_now.h>
#include <Wire.h>

// MAC del master
uint8_t macDest[6];
int conectado = 0;
int enviado = 0;

// Tiempo entre medidas
uint32_t T = 0;

esp_now_peer_info_t peerInfo;

// Callback para almacenar la mac
void receiveMAC(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  if(conectado == 0)
  {
    sscanf((char *)incomingData, "%ld", &T);
    memcpy(macDest, info->src_addr, 6);
    conectado = 1;
  }
}

void assertTransmission(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  enviado = 1;
}

// Estructura del mensaje
typedef struct struct_message {
    float temperatura;
    float humedad;
    float presion;
    int bat;
    uint8_t exterior;
} struct_message;
// Estructura para enviar los datos
struct_message datos_enviar;
void setup() {
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  WiFi.setTxPower(WIFI_POWER_15dBm);  // Reducir la potencia de emisión
  Serial.begin(115200);
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error al inicializar ESP-NOW");
  }
  // Añado el callback
  esp_now_register_recv_cb(receiveMAC);
  esp_now_register_send_cb(assertTransmission);
  // Espero hasta recibir la MAC del master
  while(!conectado) {
    delay(1);
  }
  // Cuando ya se ha conectado, añado el destino
  memset(&peerInfo, 0, sizeof(peerInfo));  // Limpia la estructura
  memcpy(peerInfo.peer_addr, macDest, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
      Serial.println("⚠ Error al agregar peer");
      return;
  }


}

void loop() {
  // esp_sleep_enable_timer_wakeup(T * 1000000);
  datos_enviar.exterior = 0;
  datos_enviar.temperatura = 0.0;
  datos_enviar.humedad = 0.0;
  datos_enviar.presion = 0.0;
  esp_err_t result = esp_now_send(macDest, (uint8_t *)&datos_enviar, sizeof(datos_enviar));

  unsigned long inicio = millis();
  while (!enviado && millis() - inicio < 500) {  // Esperar hasta 500ms
    delay(10);  // Evitar bloqueo infinito
  }

  // esp_deep_sleep_start();
}
