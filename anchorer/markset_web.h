

#include <WebServer.h>
#include "anchorer.h"

WebServer web_server_(80);
class MarksetWeb
{
public:
  MarksetWeb(Anchorer* anchorer)
  {
    const char* www_username = "test";         
    const char* www_password = "markset";  
    WebServer server(80);
    web_server_.on("/", [&]() {
      handleRoot();
    });
  
    web_server_.on("/inline", [&]() {
      web_server_.send(200, "text/plain", "this works as well");
    });
    web_server_.onNotFound([&]() {
      return this->handleNotFound();
    });
    
    web_server_.begin();

    server.on("/", [&]() {
      return this->handleRoot();
    });
    server.on("/inline", [&]() {
      server.send(200, "text/plain", "this works as well");
    });
    server.onNotFound([&]() {
      return this->handleNotFound();
    });
    server.begin();
    Serial.println("test10");
    
  }  

  void handleNotFound() {
    digitalWrite(LED, 1);
    String message = "File Not Found\n\n";
    message += "URI: ";
    message += web_server_.uri();
    message += "\nMethod: ";
    message += (web_server_.method() == HTTP_GET) ? "GET" : "POST";
    message += "\nArguments: ";
    message += web_server_.args();
    message += "\n";
  
    for (uint8_t i = 0; i < web_server_.args(); i++) {
      message += " " + web_server_.argName(i) + ": " + web_server_.arg(i) + "\n";
    }
  
    web_server_.send(404, "text/plain", message);
    digitalWrite(LED, 0);
  }
  void tick_server(){
     web_server_.handleClient();
  }
  // dumb workaround
  static void tick_server_static(void* pvParameters){
    MarksetWeb *l_pThis = (MarksetWeb *) pvParameters;
    while(true){
      l_pThis->tick_server();
    }
  }
private:

  void handleRoot() {
    digitalWrite(LED, 1);
    char temp[400];
    int sec = millis() / 1000;
    int min = sec / 60;
    int hr = min / 60;
    
    Serial.println("received root request");
  
    snprintf(temp, 300 ,
             "<html>\
    <head>\
      <meta http-equiv='refresh' content='5'/>\
      <title>ESP32 Demo</title>\
      <style>\
        body { background-color: #cccccc; font-family: Arial, Helvetica, Sans-Serif; Color: #000088; }\
      </style>\
      <script src='https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js'></script>\
    </head>\
    <body>\
      <h1>Hello from ESP32!</h1>\n\
      <p><button type=\"button\" onclick=\"$.post({url: 'api/anchor/down'})\">Down</button></p>\
    </body>\
  </html>");
    web_server_.send(200, "text/html", temp);
    digitalWrite(LED, 0);
  }

};


 
