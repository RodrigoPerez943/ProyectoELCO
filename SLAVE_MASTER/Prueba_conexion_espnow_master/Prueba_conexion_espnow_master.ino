#include <WiFi.h>
#include <esp_now.h>


// Prueba para el master, la mac destino es broadcast
uint8_t macDestino[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// Estructura del mensaje
typedef struct struct_message {
    float temperatura;
    float humedad;
    float presion;
    uint8_t exterior;
} struct_message;

// Flag para ver si ya se ha configurad el tiempo entre medidas
// int configurado = 0;

uint8_t buffer_RX[40];
uint8_t index_RX = 0;

// Configuro lo que pasa cuando se recibe
void receiveDATA(const esp_now_recv_info_t *info, const uint8_t *incomingData, int len) {
  struct_message datos_recibidos;
  memcpy(&datos_recibidos, incomingData, sizeof(datos_recibidos));
  char buffer[200];
  memset(buffer, 0, sizeof(buffer));
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
  Serial0.println(buffer);
}

void actualizaTiempo()
{
  if(index_RX == 0)
  {
    memset(buffer_RX, 0, sizeof(buffer_RX));
  }
  while(Serial.available())
  {
    int aux = Serial0.read();
    Serial.println("DATO");
    if(aux == '\n')
    {
      break;
    }
    buffer_RX[index_RX++] = aux;
  }
  index_RX = 0;
}

void setup() {
  Serial0.begin(115200);
  WiFi.mode(WIFI_STA); // Configurar Wi-Fi en modo estación
  WiFi.setTxPower(WIFI_POWER_15dBm);  // Reducir la potencia de emisión
  if (esp_now_init() != ESP_OK) {
    Serial0.println("Error al inicializar ESP-NOW");
  }
  // Recepción de medidas
  esp_now_register_recv_cb(receiveDATA);
  // Emisión de mensajes
  esp_now_peer_info_t peerInfo;
  memcpy(peerInfo.peer_addr, macDestino, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial0.println("⚠ Error al agregar peer de Broadcast");
    return;
  }
    memset(buffer_RX, 0, sizeof(buffer_RX));
  // Configuración del tiempo entre medidas 
  while(1)
  {
    if (Serial0.available() > 0) 
    {
      int aux = Serial0.read();
      if(aux == '\n')
      {
        break;
      }
      buffer_RX[index_RX++] = aux;
    }
  }
  index_RX = 0;
  Serial0.onReceive(actualizaTiempo);
}

void loop() {
  esp_err_t result = esp_now_send(macDestino, buffer_RX, sizeof(buffer_RX));
  delay(1000);
}