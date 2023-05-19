#include <heltec.h>
#include <Arduino.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include "markset_web.h"

const char* ssid = "markus";          // Your WiFi SSID
const char* password = "1234567890";  // Your WiFi Password

// define two tasks for Blink & AnalogRead
void StartWifi(){
  // Set WiFi to station mode and disconnect from an AP if it was previously connected
  Serial.println("test");
  WiFi.disconnect(true);
  delay(1000);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoConnect(true);
  int n = WiFi.scanNetworks();
  Serial.println("scan done");
  if (n == 0) {
      Serial.println("no networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      // Print SSID and RSSI for each network found
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":"*");
      delay(10);
    }
  }
  Serial.println("");
  IPAddress ip(10, 42, 0, 2); 
  IPAddress ip1(10, 42, 0, 1); 
  IPAddress ip2(255, 255, 255, 0); 
  WiFi.config(ip, ip1, ip2);  
  WiFi.begin(ssid, password);
  delay(100);
  Heltec.display -> clear();
  Serial.println("test");
  bool connected = false;
  int notConnectedCounter = 0;
  while(!connected){
    Serial.println("TaskCheckWifi.");
    Heltec.display -> clear();
    delay(500);
    
    Serial.printf("checkin %s", ssid);
    if(WiFi.status() == WL_CONNECTED)
    {
      Serial.printf("wifi good %s", WiFi.localIP().toString());
      Heltec.display -> drawString(0, 0, "Connecting...OK.");
      delay(500);
      Heltec.display -> drawString(0, 20, WiFi.localIP().toString());
      connected = true;
    }
    else
    {
      Heltec.display -> drawString(0, 0, "Connecting...Failed");
      
      notConnectedCounter++;
      if(notConnectedCounter > 5) { // Reset board if not connected after 5s
          Serial.println("Resetting due to Wifi not connecting...");
          ESP.restart();
      }
    }
    Heltec.display -> display();
    delay(1000);
  }
}



Anchorer* anchorer;
MarksetWeb* markset_web;

void setup() {
  pinMode(LED,OUTPUT);
  digitalWrite(LED,HIGH);

  Serial.begin(115200);
  Heltec.begin(true /*DisplayEnable Enable*/, false /*LoRa Enable*/, true /*Serial Enable*/);

  Heltec.display->flipScreenVertically();
  
  delay(300);
  Heltec.display->clear();
  Serial.println("test1");
  StartWifi();
  
  anchorer = new Anchorer();
  markset_web = new MarksetWeb(anchorer);
  
  
  
//  xTaskCreate(
//    MarksetWeb::tick_server_static
//    ,  "TaskWebserver"   // A name just for humans
//    ,  8092 // This stack size can be checked & adjusted by reading the Stack Highwater
//    ,  markset_web
//    ,  3 // Priority, with 3 (configMAX_PRIORITIES - 1) being the highest, and 0 being the lowest.
//    ,  NULL );

//  xTaskCreate(
//    Anchorer::tick_server_static
//    ,  "TaskAnchorer"
//    ,  2048  // Stack size
//    ,  anchorer
//    ,  2  // Priority
//    ,  NULL );
    

}

void loop() {
  while(true){
    markset_web->tick_server();
  }
}
