#define TCP_MSS whatever
#define LWIP_IPV6 whatever
#define LWIP_FEATURES whatever
#define LWIP_OPEN_SRC whatever
#include <coap_client.h>
#include <coap_server.h>
#include <ESP8266WiFi.h>


coapClient coap;

//WiFi connection info
const char* ssid = "TP-LINK0023";
const char* password = "20202020";


//ip address and default port of coap server 
IPAddress ip(192,168,1,2);
int port =5683;

int PIR_PIN = 5;
const int ledGPIO1 = 4; // RED LED
const int ledGPIO2 = 0; // GREEN LED
void callback_response(coapPacket &packet, IPAddress ip, int port);


void callback_response(coapPacket &packet, IPAddress ip, int port) {
    char p[packet.payloadlen + 1];
    memcpy(p, packet.payload, packet.payloadlen);
    p[packet.payloadlen] = NULL;

    
 if(packet.type==3 && packet.code==0){
      Serial.println("ping ok");
    }

    Serial.println(p);
}
void setup() {
    pinMode(PIR_PIN, INPUT);
    pinMode(ledGPIO1, OUTPUT);
    pinMode(ledGPIO2, OUTPUT);
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    Serial.println(" ");

    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
    //delay(500);
    yield();
    Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected");
   
    Serial.println(WiFi.localIP());

    coap.response(callback_response);

   
    coap.start();
    }
void loop() {
 	bool state;
   digitalWrite(ledGPIO1, HIGH); // RED IS ON
   digitalWrite(ledGPIO2, LOW); // GREEN IS OFF  
 	 if (digitalRead(PIR_PIN) == HIGH) {           
    	int msgid =coap.post(ip,port,"esp8266_2_pir","1",strlen("1"));
     digitalWrite(ledGPIO1, LOW); // RED IS OFF
     digitalWrite(ledGPIO2, HIGH); // GREEN IS ON
    	Serial.println("LED ON");
    	delay(5000);
 	 } 
  else {
      int msgid =coap.post(ip,port,"esp8266_2_pir","0",strlen("0"));
      digitalWrite(ledGPIO1, HIGH); // RED IS ON
      digitalWrite(ledGPIO2, LOW); // GREEN IS OFF
      Serial.println("LED OFF");
      delay(500);             
  }
  state= coap.loop();
  delay(1000);

}
