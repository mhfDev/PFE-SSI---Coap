#define TCP_MSS whatever
#define LWIP_IPV6 whatever
#define LWIP_FEATURES whatever
#define LWIP_OPEN_SRC whatever
#include <ArduinoJson.h>
#include <coap_client.h>
#include <coap_server.h>
#include <ESP8266WiFi.h>
#include <SPI.h>
#include <MFRC522.h>
#include <AES.h>
#include <AESLib.h>
#include <AES_config.h>
#include <Base64.h>

coapClient coap;
AESLib aesLib;

//WiFi connection info
const char* ssid = "TP-LINK0023";
const char* password = "20202020";


//ip address and default port of coap server 
IPAddress ip(192,168,1,2);
int port =5683;

const int SS_PIN = 2;
const int RST_PIN = 0;
StaticJsonBuffer<200> jsonBuffer;
JsonObject& root = jsonBuffer.createObject();
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

long now = millis();
long lastMeasure = 0;

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

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}
void setup() {
   
  Serial.begin(115200);   // Initiate a serial communication (9600)
  SPI.begin();      // Initiate  SPI bus
  setup_wifi();
  mfrc522.PCD_Init();   // Initiate MFRC522
  Serial.println("Approximate your card to the reader...");
  Serial.println();
  coap.response(callback_response);
  coap.start();
  }


void loop() 
{

  bool state;
  now = millis();
  // Publishes new temperature and humidity every 10 seconds
  
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  lastMeasure = now;
  //Show UID on serial monitor
  
  Serial.print("UID tag :");
  String content;
  byte letter;
  String etat;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "19 7A A3 B8") //change here the UID of the card/cards that you want to give access 
  {
    etat="1";
    Serial.println("Authorized access");
    Serial.println();
  }
 
  else {
    etat="0";
    Serial.println("Access denied");
  }
  string k="abcdefghijklmnop"
  byte key[k.length()];
  k.getBytes(key, k.length());
  byte my_iv[16] = { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  root["uid"] = content;
  root["status"] = etat;
  char* path = "esp8266_1_rfid";
  String m="{ \"uid\": \""+content+"\",\"status\" :"+etat+"}";
  unsigned long ms = micros ();
  String encMsg = aesLib.encrypt(m, key, my_iv);
  Serial.print("Encryption took: ");
  Serial.println(micros() - ms);  
  //Serial.println("encMsg: " + encMsg);
  char dataChar[encMsg.length() + 1];
  encMsg.toCharArray(dataChar, encMsg.length() + 1);
  //client.publish("esp8266_1_rfid", msg);
  int msgid =coap.post(ip,port,path,dataChar,m.length());
  Serial.println("\nThe message sent to coap server is:");
  Serial.print(encMsg);
  Serial.println("---------------------");
  Serial.print("status: ");
  Serial.print(etat);
  Serial.print(" \t UID: ");
  Serial.print(content);
  Serial.println(" ");
  //coap.get(ip,port,path);
  state= coap.loop();
  delay(3000);
}
