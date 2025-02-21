#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>

// Instanciar sensores
Adafruit_AHTX0 aht20;
Adafruit_BMP280 bmp280;

void setup() {
    Serial.begin(115200);
    Wire.begin(35, 34);  // SDA = GPIO6, SCL = GPIO7

    // Inicializar AHT20
    if (!aht20.begin()) {
        Serial.println("No se encontró el sensor AHT20.");
        while (1);
    }
    Serial.println("AHT20 inicializado correctamente.");

    // Inicializar BMP280
    if (!bmp280.begin(0x76)) {  // Asegúrate de usar la dirección correcta (0x76 o 0x77)
        Serial.println("No se encontró el sensor BMP280.");
        while (1);
    }
    Serial.println("BMP280 inicializado correctamente.");
}

void loop() {
    // Lectura del AHT20
    sensors_event_t temp_event, humidity_event;
    aht20.getEvent(&humidity_event, &temp_event);

    // Lectura del BMP280
    float temperatureBMP = bmp280.readTemperature();
    
    // Imprimir resultados
    Serial.print("AHT20 - Temperatura: "); Serial.print(temp_event.temperature); Serial.println(" °C");
    Serial.print("AHT20 - Humedad: "); Serial.print(humidity_event.relative_humidity); Serial.println(" %");
    
    Serial.print("BMP280 - Temperatura: "); Serial.print(temperatureBMP); Serial.println(" °C");

    Serial.println("----------------------");
    delay(2000);  // Esperar 2 segundos
}
