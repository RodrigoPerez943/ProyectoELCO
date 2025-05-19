#include <WiFi.h>
#include <esp_now.h>
#include <esp_sleep.h>
#include <OneWire.h>                
#include <DallasTemperature.h>

OneWire ourWire(2);                //Se establece el pin 2  como bus OneWire
 
DallasTemperature sensors(&ourWire); //Se declara una variable u objeto para nuestro sensor

// MAC del master
uint8_t macDest[6];
int conectado = 0;
int enviado = 0;

// Tiempo entre medidas
uint32_t T = 0;

esp_now_peer_info_t peerInfo;

// Callback para almacenar la mac
void receiveMAC(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  // memcpy(macDest, incomingData, 6);
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
    uint8_t exterior;
} struct_message;
// Estructura para enviar los datos
struct_message datos_enviar;

void setup() {
  delay(1000);
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  // Serial.begin(115200);
  sensors.begin();   //Se inicia el sensor
  if (esp_now_init() != ESP_OK) {
    // Serial.println("Error al inicializar ESP-NOW");
    while(true);
  }
  // Añado el callback
  esp_now_register_recv_cb(receiveMAC);
  esp_now_register_send_cb(assertTransmission);
  while(!conectado) {
    delay(1);
  }
  // Cuando ya se ha conectado, añado el destino
  memset(&peerInfo, 0, sizeof(peerInfo));  // Limpia la estructura
  memcpy(peerInfo.peer_addr, macDest, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
      // Serial.println("⚠ Error al agregar peer");
      return;
  }
  if (sensors.getDeviceCount() == 0) {
    // Serial.println("DS18B20 not detected. Please check wiring. Freezing.");
    while(true);
  }
}

void loop() {
  esp_sleep_enable_timer_wakeup(T * 1000000);
  datos_enviar.exterior = 1;
  sensors.requestTemperatures();   //Se envía el comando para leer la temperatura
  datos_enviar.temperatura = sensors.getTempCByIndex(0);
  // Serial.println(datos_enviar.temperatura);
  // Serial.println(T);
  datos_enviar.humedad = 0.0;
  datos_enviar.presion = 0.0;
  esp_err_t result = esp_now_send(macDest, (uint8_t *)&datos_enviar, sizeof(datos_enviar));
  unsigned long inicio = millis();
  while (!enviado && millis() - inicio < 500) {  // Esperar hasta 500ms
    delay(10);  // Evitar bloqueo infinito
  }


  esp_deep_sleep_start();
}
