#include "string.h"

#include <SPI.h>
#include "Adafruit_MAX31855.h"

#define MAXDO   12
#define MAXCS   10
#define MAXCLK  13

// initialize the Thermocouple
Adafruit_MAX31855 thermocouple(MAXCLK, MAXCS, MAXDO);

unsigned long now = 0;
unsigned long prev = 0;
unsigned long elapsed = 0;

#define SSR_PIN 2

int duty = 0;

uint8_t state = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(SSR_PIN, OUTPUT);
  Serial.println("RESET!");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0)
  {
    char a = Serial.read();
    if(a == 'p')
    {
      
    }
  }
  now = millis();
  elapsed = now - prev;
  
  // one second elapsed
  if(elapsed >= 1000)
  {
    if(duty > 0)
    {
      digitalWrite(SSR_PIN, HIGH);
    }
    prev = now;

    //send measurement
    Serial.println(thermocouple.readCelsius());
  }
  else if(elapsed >= (duty * 10))
  {
    digitalWrite(SSR_PIN, LOW);
  }
}
