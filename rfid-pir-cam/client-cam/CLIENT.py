import socket,os,time,Takephoto
import json
from cv2 import cv2
import sqlite3

from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from pybase64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad



url = "coap://192.168.1.2:5683/" # default path
host, port, path = parse_uri(url)


client = HelperClient(server=(host, port))

result = {
    'id': 0,
    'uid': '',
    'nom': '',
    'prenom': ''
}
key = 'abcdefghijklmnop'


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainner/trainner.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def cam_request():
    response = client.get("/esp8266_3_capture");
    payload = response._payload;
    if payload == "1":
    	global result
    	print("Taking Photo")
    	cam = cv2.VideoCapture(0)
    	stat = True
    	while stat:
    		s, frame = cam.read()
    		im = frame
    		gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    		faces = faceCascade.detectMultiScale(gray,1.3,5)
    		for (x, y, w, h) in faces:
    			cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    			if s:
    				cv2.imwrite("photo/shot.jpg",im)
    				stat = False
    			break
    	cam.release()
    	cv2.destroyAllWindows()
    	img = cv2.imread('photo/shot.jpg', 0)
    	faces=faceCascade.detectMultiScale(img, 1.2,5)
    	for(x,y,w,h) in faces:
    		Id, conf = recognizer.predict(img[y:y+h,x:x+w])
    		if(conf>=60):
    			Id=0
    		print(Id)
    	if(Id != 0):
    		con = sqlite3.connect('imEtudiants.db')
    		con.row_factory = dict_factory
    		c = con.cursor()
    		c.execute('SELECT * from etudiants where id={}'.format(Id))
    		result = c.fetchone()
    		c.close()
    		result = json.dumps(result)
    		# print(result)
    # Publish the associated UID to server
    	cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
        ct_bytes = cipher.encrypt(pad(result, AES.block_size))
        ct = b64encode(ct_bytes).decode('utf-8')
        print("message posted:",ct)
        client.post("/esp8266_3_cam", ct)
    	# print("message posted")
    	result = {
            'id': 0,
            'uid': '',
            'nom': '',
            'prenom': ''
            }

cam_request()