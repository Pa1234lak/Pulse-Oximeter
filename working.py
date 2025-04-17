#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include "MAX30100_PulseOximeter.h"

#define REPORTING_PERIOD_MS 1000
#define MIN_VALID_HEART_RATE 70
#define MAX_VALID_HEART_RATE 100

LiquidCrystal_I2C lcd(0x27, 16, 2);
PulseOximeter pox;

uint32_t tsLastReport = 0;
bool fingerDetected = false;
int failureCount = 0;

void onBeatDetected() {
    Serial.println("♥ Beat Detected!");
}

void setup() {
    // Start serial communication
    Serial.begin(115200);
    
    // Initialize I2C and LCD
    Wire.begin();
    lcd.init();
    lcd.backlight();
    
    // Clear and show initial message
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Initializing");
    lcd.setCursor(0, 1);
    lcd.print("Pulse Oximeter");
    delay(1000);

    // Attempt sensor initialization
    Serial.println("Attempting to initialize MAX30100");
    
    if (!pox.begin()) {
        lcd.clear();
        lcd.print("Sensor Error!");
        Serial.println("Sensor initialization failed!");
        while(1); // Halt
    }
    
    // Configure sensor
    pox.setIRLedCurrent(MAX30100_LED_CURR_24MA);
    pox.setOnBeatDetectedCallback(onBeatDetected);
    
    // Clear initial message
    lcd.clear();
    lcd.print("Place Finger");
}

void loop() {
    // Update the pulse oximeter
    pox.update();
    
    // Get current readings
    float heartRate = pox.getHeartRate();
    float spO2 = pox.getSpO2();
    
    // Check if readings are valid
    if (heartRate > 0 && spO2 > 0 && 
        heartRate >= MIN_VALID_HEART_RATE && 
        heartRate <= MAX_VALID_HEART_RATE) {
        
        // Periodic reporting
        if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
            // Debug serial output
            Serial.print("Heart rate: ");
            Serial.print(heartRate);
            Serial.print(" bpm | SpO2: ");
            Serial.print(spO2);
            Serial.println(" %");
            
            // LCD Display
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("HR: ");
            lcd.print(heartRate, 1);
            lcd.print(" bpm");
            
            lcd.setCursor(0, 1);
            lcd.print("SpO2: ");
            lcd.print(spO2, 1);
            lcd.print("%");
            
            tsLastReport = millis();
            
            // Optional: Wait to keep reading visible
            delay(3000);
            
            // Reset display
            lcd.clear();
            lcd.print("Place Finger");
        }
    } else {
        // No valid reading
        if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
            lcd.clear();
            lcd.print("No finger");
            lcd.setCursor(0, 1);
            lcd.print("detected");
            
            Serial.println("No valid reading - Check finger placement");
            
            tsLastReport = millis();
        }
    }
    
    delay(10);
}
