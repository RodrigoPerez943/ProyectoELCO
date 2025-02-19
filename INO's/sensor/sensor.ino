#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>

// Crear objetos para los sensores
Adafruit_AHTX0 aht20;
Adafruit_BMP280 bmp280;

// Presión estándar al nivel del mar (1013.25 hPa), ajusta si es necesario
#define SEA_LEVEL_PRESSURE 1013.25 

void setup() {
    Serial.begin(115200);
    Wire.begin(); // Inicializa I2C con los pines por defecto del ESP32

    Serial.println("\n--- Inicializando sensores ---");

    // Verificar si el AHT20 está presente
    if (!aht20.begin()) {
        Serial.println("❌ Error: AHT20 no encontrado. Verifica las conexiones.");
    } else {
        Serial.println("✅ AHT20 detectado correctamente.");
    }

    // Verificar si el BMP280 está presente
    if (!bmp280.begin(0x77)) {  // Dirección I2C típica del BMP280 (puede ser 0x76 o 0x77)
        Serial.println("❌ Error: BMP280 no encontrado. Verifica las conexiones.");
    } else {
        Serial.println("✅ BMP280 detectado correctamente.");
        bmp280.setSampling(Adafruit_BMP280::MODE_NORMAL,
                           Adafruit_BMP280::SAMPLING_X2,   // Oversampling temperatura
                           Adafruit_BMP280::SAMPLING_X16,  // Oversampling presión
                           Adafruit_BMP280::FILTER_X16,    // Filtro
                           Adafruit_BMP280::STANDBY_MS_500); // Tiempo en espera
    }
}

void loop() {
    Serial.println("\n--- Lectura de sensores ---");

    // Lectura del AHT20
    sensors_event_t humidity, temp;
    aht20.getEvent(&humidity, &temp);
    Serial.print("🌡️  Temp AHT20: "); Serial.print(temp.temperature); Serial.println(" °C");
    Serial.print("💧 Humedad: "); Serial.print(humidity.relative_humidity); Serial.println(" %");

    // Lectura del BMP280
    float temperatureBMP = bmp280.readTemperature();
    float pressure = bmp280.readPressure() / 100.0F; // Convierte a hPa
    float altitude = bmp280.readAltitude(SEA_LEVEL_PRESSURE); // Estima altitud con presión al nivel del mar

    Serial.print("🌡️  Temp BMP280: "); Serial.print(temperatureBMP); Serial.println(" °C");
    Serial.print("🌎 Presión: "); Serial.print(pressure); Serial.println(" hPa");
    Serial.print("⛰️  Altitud estimada: "); Serial.print(altitude); Serial.println(" m");

    delay(2000); // Esperar 2 segundos antes de la siguiente lectura
}
