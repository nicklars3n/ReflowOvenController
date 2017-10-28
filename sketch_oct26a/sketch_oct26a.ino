#include "string.h"

unsigned long now = 0;
unsigned long prev = 0;
unsigned long elapsed = 0;

int duty = 0;

String buff = "";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.println("RESET!");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0)
  {
    char a = Serial.read();
    if(a == '\n')
    {
      int temp = buff.toInt();
      
      if(temp >= 0 && temp <= 100)
      {
        duty = temp;
      }
      buff = "";
    }
    else
    {
      buff.concat(a);
    }
  }
  now = millis();
  elapsed = now - prev;
  
  // one second elapsed
  if(elapsed >= 1000)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    prev = now;
  }
  else if(elapsed >= (duty * 10))
  {
    digitalWrite(LED_BUILTIN, LOW);
  }
}
