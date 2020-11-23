import network
import machine
import microcoapy
from machine import Pin,SPI
import mfrc522

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

_MY_SSID = 'TP-LINK0023'
_MY_PASS = '20202020'
_SERVER_IP = '192.168.201.3'
_SERVER_PORT = 5683  # default CoAP port
_COAP_POST_URL = 'esp8266_1_rfid'

spi = SPI(1, baudrate=2500000, polarity=0, phase=0)
spi.init()
rdr = mfrc522.MFRC522(spi=spi, gpioRst= 0, gpioCs= 2)

def connectToWiFi():
    nets = wlan.scan()
    for net in nets:
        ssid = net[0].decode("utf-8")
        if ssid == _MY_SSID:
            print('Network found!')
            wlan.connect(ssid, _MY_PASS)
            while not wlan.isconnected():
                machine.idle()  # save power while waiting
            print('WLAN connection succeeded!')
            break

    return wlan.isconnected()


# def sendPostRequest(client):
#     # About to post message...
#     messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, "test",
#                                    None, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
#     print("[POST] Message Id: ", messageId)

    # wait for respose to our request for 2 seconds
    client.poll(10000)
def receivedMessageCallback(packet, sender):
    print('Message received:', packet.toString(), ', from: ', sender)

connectToWiFi()

client = microcoapy.Coap()
client.discardRetransmissions = True
#client.debug = False
# setup callback for incoming respose to a request
client.resposeCallback = receivedMessageCallback

# Starting CoAP...
client.start()
print("READING CARD ........")
(stat, tag_type) = rdr.request(rdr.REQIDL)
if stat == rdr.OK:
    (stat, raw_uid) = rdr.anticoll()
    if stat == rdr.OK:
        print("********************************")
        print("* - CARTE Detected")
        print("* - type of CARTE : %02x" % tag_type)
        print("* - UID : %02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
        print("********************************")
        print("")
        etat = "1" 
        m = "{ \"uid\": \"%02x%02x%02x%02x\"" %(raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]) +",\"status\" :" + etat + "}";
        print ("msg publish : ",m)
        # c.publish(topic,m)
        messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, m,
                                   None, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
        print("[POST] Message Id: ", messageId)

        # wait for respose to our request for 2 seconds
        client.poll(10000)


# stop CoAP
client.stop()