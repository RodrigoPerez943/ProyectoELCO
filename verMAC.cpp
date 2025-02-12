#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  // Inicializa WiFi en modo STA (o AP, según tu necesidad)
  WiFi.mode(WIFI_STA);
  
  // Imprime la dirección MAC en el monitor serie
  Serial.print("Dirección MAC del hub: ");
  Serial.println(WiFi.macAddress());
}

void loop() {
  // Tu código para recibir datos con ESP-NOW, etc.
}
