import network
import machine
import microcoapy
from machine import Pin

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

pin = machine.Pin(INPUTPIN, machine.Pin.IN, machine.Pin.PULL_UP)
ledGPIO1 = 4 # RED LED
ledGPIO2 = 2  # GREEN LED
led1 = machine.Pin(ledGPIO1, machine.Pin.OUT)
led2 = machine.Pin(ledGPIO2, machine.Pin.OUT)

_MY_SSID = 'TP-LINK0023'
_MY_PASS = '20202020'
_SERVER_IP = '192.168.201.3'
_SERVER_PORT = 5683  # default CoAP port
_COAP_POST_URL = 'esp8266_2_pir'


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


def sendPostRequest(client,data):
    # About to post message...
    messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, data,
                                   None, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
    print("[POST] Message Id: ", messageId)

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
if pin.value() == 1:
    print(" LED ON")
    led2.value(1)
    led1.value(0)
    messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, "1",
                                 None, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
    print("[POST] Message Id: ", messageId)

    # wait for respose to our request for 2 seconds
    client.poll(10000)
if pin.value() == 0:
    print(" LED OFF")
    led2.value(0)
    led1.value(1)
    messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, "0",
                                 None, microcoapy.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
    print("[POST] Message Id: ", messageId)

    # wait for respose to our request for 2 seconds
    client.poll(10000)

# stop CoAP
client.stop()