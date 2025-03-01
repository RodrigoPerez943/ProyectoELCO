#include <WiFi.h>
#include <esp_now.h>
#include <Wire.h>
#include <AHT20.h>
#include <Adafruit_BMP280.h>
#include <esp_sleep.h>

// Estructuras para medir
AHT20 aht20;
Adafruit_BMP280 bmp280;

// El led me sirve para ver si se ha conectado
// #define GPIOLED 8

// MAC del master
uint8_t macDest[6];
int conectado = 0;
int enviado = 0;

esp_now_peer_info_t peerInfo;

// Callback para almacenar la mac
void receiveMAC(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  // memcpy(macDest, incomingData, 6);
  if(conectado == 0)
  {
    // uint8_t broad[] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
    memcpy(macDest, info->src_addr, 6);
    conectado = 1;
  }
}

void assertTransmission(const uint8_t *mac_addr, esp_now_send_status_t status)
{
  enviado = 1;
  Serial.println("HOLA");
  Serial.flush();
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
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  // Configuro el led para que se encienda cuando esté conectado
  // pinMode(GPIOLED, OUTPUT);
  // El led queda apagado hasta que se conecte.
  // digitalWrite(GPIOLED, HIGH); 
  Serial.begin(115200);
  // delay(5000);
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
  // digitalWrite(GPIOLED, LOW);

  // Configuracion para medir
  Wire.begin(8,9); 
    if (aht20.begin() == false)
  {
    Serial.println("AHT20 not detected. Please check wiring. Freezing.");
    while(true);
  }
  if(bmp280.begin() == false)
  {
    Serial.println("BMP280 not detected. Please check wiring. Freezing.");
    while(true);
  }
}
void loop() {
  esp_sleep_enable_timer_wakeup(5 * 1000000);
  datos_enviar.exterior = 0;
  datos_enviar.temperatura = aht20.getTemperature();
  datos_enviar.humedad = aht20.getHumidity();
  datos_enviar.presion = bmp280.readPressure()/100;
  esp_err_t result = esp_now_send(macDest, (uint8_t *)&datos_enviar, sizeof(datos_enviar));
  unsigned long inicio = millis();
  while (!enviado && millis() - inicio < 500) {  // Esperar hasta 500ms
    delay(10);  // Evitar bloqueo infinito
  }


  esp_deep_sleep_start();
}

