"""
    Created by  :    G1 : {- LOTFI Hamza / RHBECH Amine }
                     G2 : {- FDIL Mehdi / ELHAIDI Mourad }

"""

from flask import Flask, render_template, request ,jsonify, url_for
import json, sqlite3, time, sys, requests
from multiprocessing import Process, Value
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from pybase64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

url = "coap://127.0.0.1:5683/"
# url = "coap://192.168.1.2:5683/" # default path
host, port, path = parse_uri(url)


client = HelperClient(server=(host, port))


app = Flask(__name__)

rfid_detected = 0
ledpir = 0
cam_data = { "cam_state" : 0, "cam_detected" :0, "ledcam" :0 }

student_data = {
    'id': 0,
    'uid': '',
    'nom': '',
    'prenom': ''
}

current_uid = ""

pins = {
    1 : {'name' : 'vert', 'board' : 'esp8266', 'topic' : 'esp8266_1_1/', 'state' : 'False'},
    2 : {'name' : 'rouge', 'board' : 'esp8266', 'topic' : 'esp8266_1_2/', 'state' : 'False'},
    3 : {'name' : 'blanche', 'board' : 'esp8266', 'topic' : 'esp8266_1_3/', 'state' : 'False'}
    }
key = 'abcdefghijklmnop'
paylad='pAewLNxHRrY59OIIPsvJnA=='
paylod='soMMvCLD+TfaK+ysk/n9vTqSAF6v14ABQ864i104xefnIHaUNMXwoLWdip8rmHXG'

@app.route('/')
def index():
    global rfid_detected
    global ledpir
    global current_uid
    rfid_detected = 0
    ledpir = 0
    current_uid = ""
    student_data['id'] = 0
    student_data['uid'] = ''
    student_data['nom'] = ''
    student_data['prenom'] = ''
    cam_data["cam_state"] = 0
    cam_data["cam_detected"] = 0
    cam_data["ledcam"] = 0
    return render_template('index.html')


@app.route("/pir/change", methods=['GET'])
def pir_state():
    global ledpir

    ledpir = int(request.args.get('status'))
    return jsonify(state="ledpir is changed to {}".format(ledpir))


@app.route("/rfid/change", methods=['GET'])
def rfid_state():
    global rfid_detected

    rfid_detected = int(request.args.get('status'))
    return jsonify(state="rfid_detected is changed to {}".format(rfid_detected))


@app.route("/cam/change", methods=['GET'])
def cam_state():
    global cam_data

    cam_data["cam_detected"] = int(request.args.get('cam_detected'))
    cam_data["cam_state"] = int(request.args.get('cam_state'))
    cam_data["ledcam"] = int(request.args.get('ledcam'))
    print ("hello from cam_state request management ", cam_data)
    return jsonify(state="cam_detected is changed to {}".format(cam_data))

@app.route("/student/change", methods=['GET'])
def student_state():
    global student_data

    student_data["id"] = request.args.get('id')
    student_data["uid"] = request.args.get('uid')
    student_data["nom"] = request.args.get('nom')
    student_data["prenom"] = request.args.get('prenom')
    print ("hello from student_state request management ",student_data)
    return jsonify(state="student_data is changed to {}".format(student_data))


@app.route('/data',methods=['GET', 'POST'])
def data():
    return data_rfid()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def data_rfid():
    global rfid_detected
    global ledpir
    global current_uid
    print ("IN data_rfid LEDPIR = ",ledpir, "AND rfid_detected = ", rfid_detected)
    rfid = []
    if(ledpir == 1 and rfid_detected == 1):
        conn = sqlite3.connect('sensordata.db')
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute('SELECT UID, STATUS FROM rfid_readings ORDER BY id DESC LIMIT 1')
        readings = c.fetchall()
        for row in readings:
            rfid.append(row["UID"])
            rfid.append(row["STATUS"])
        conn.close()
    return jsonify(rfid=rfid, ledpir=ledpir, cam_data=cam_data, student_data=student_data , current_uid=current_uid)
 

def change_ledpir_status(status):
    print ("Hello from change_ledpir_status")
    PARAMS = {'status': status}
    r = requests.get('http://127.0.0.1:8181/pir/change', params=PARAMS)
    time.sleep(0.5)
    data = r.json()
    print ("Result of request is: ",data['state'])


def change_rfid_status(status):
    print ("Hello from change_rfid_status")
    PARAMS = {'status': status}
    r = requests.get('http://127.0.0.1:8181/rfid/change', params=PARAMS)
    time.sleep(0.5)
    data = r.json()
    print ("Result of request is: ",data['state'])


def change_cam_data(data):
    print ("Hello from change_cam_data")
    PARAMS = data
    r = requests.get('http://127.0.0.1:8181/cam/change', params=PARAMS)
    time.sleep(0.5)
    data = r.json()
    print ("Result of request is: ",data)


def change_student_data(data):
    print ("Hello from change_student_data")
    PARAMS = data
    r = requests.get('http://127.0.0.1:8181/student/change', params=PARAMS)
    time.sleep(0.5)
    data = r.json()
    print ("Result of request is: ",data)


def get_data():
    print ("hello from get_data")
    r = requests.get('http://127.0.0.1:8181/data')
    data = r.json()
    print ("data is ", data)
    return data


def handle_pir_request():
    global pins
    global key
    global paylad
    response = client.get("/esp8266_2_pir")
    payload = response._payload
    ctd = b64decode(paylad)
    cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
    dat= unpad(cipher.decrypt(ctd), AES.block_size)
    client.post(pins[3]['topic'], dat)
    if dat == "1":
        change_ledpir_status("1")
        pins[3]['state'] = 'True'
        time.sleep(1)
        handle_rfid_request()
    else:
        change_ledpir_status("0")
        pins[3]['state'] = 'False'
        time.sleep(1)
        handle_pir_request()


def handle_rfid_request():
    global current_uid
    global cam_data

    response = client.get("/esp8266_1_rfid")
    payload = eval(response._payload)
    ctd = b64decode(paylod)
    cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
    dat= unpad(cipher.decrypt(ctd), AES.block_size)
    d=eval(dat)
    print ("RFID payload value is ", d,"type is ", type(d))
    if cam_data["cam_state"] == 0:
        change_rfid_status("1") # change rfid status to 1 (ON)
        conn = sqlite3.connect('sensordata.db')
        c = conn.cursor()
        c.execute('INSERT INTO rfid_readings (UID, STATUS, currentdate, currentime) VALUES ("{}","{}",date("now"),time("now"))'.format(payload["uid"],payload["status"]))
        conn.commit()
        conn.close()
        if d["status"] == "1":
            if current_uid == '' or current_uid != d['uid'].strip():
                current_uid = d['uid'].strip()
                change_cam_data({"ledcam": "0", "cam_detected": "0", "cam_state": "1"}) # change cam data
                client.post("/esp8266_3_capture", "1")
                time.sleep(1)
                print ("CAM DATA is ", cam_data)
                handle_cam_request()
        else:
            change_cam_data({"ledcam": "0", "cam_detected": "0", "cam_state": "0"}) # change cam data
            time.sleep(1)
            handle_pir_request()     


def handle_cam_request():
    global current_uid
    global cam_data
    global rfid_detected
    print ("hello from handle_cam_request")
    data = get_data()
    time.sleep(0.5)
    if data["cam_data"]["cam_state"] == 1:
        print ("-"*100)
        print ("cam_state is equal to 1")
        # rfid_response = client.get("/esp8266_1_rfid")
        # rfid_payload = eval(rfid_response._payload) # convert string to dict
        # print "handle_cam_request rfid payload value is ", rfid_payload
        cam_response = client.get('/esp8266_3_cam')
        ctd = b64decode(cam_response._payload)
        cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
        dat= unpad(cipher.decrypt(ctd), AES.block_size)
        cam_payload = eval(dat) # covert string to dict
        print ("#"*50)
        print (current_uid)
        print ("-"*25)
        print (cam_payload['uid'])
        print ("*-*"*25)
        print (bool(current_uid==cam_payload['uid']))
        print ("#"*50)
        if current_uid == cam_payload['uid']: # compare with the uid exist in cam_payload
            print ("handle_cam_request cam payload value is ", cam_payload)
            change_cam_data({"ledcam": "1", "cam_detected": "1", "cam_state": "1"}) # change cam data
            change_student_data(cam_payload)
        else:
            change_cam_data({"ledcam": "0", "cam_detected": "1", "cam_state": "0"}) # change cam data
            change_rfid_status("0")
            current_uid = ""
    # else:
    #     print "cam_state is equal to 0"
    #     print "data value is ", data
    #     print "cam_data is ",data["cam_data"]
    #     print "current_uid is ", current_uid
    #     sys.exit(0)


def handle_requests():
    while True:
        handle_pir_request()



if __name__ == "__main__":
    try:
        print ("starting the  main")
        p = Process(target=handle_requests)
        p.start()
        app.run(host='0.0.0.0', port=8181, debug=False, use_reloader=False)
        p.join()
    except (Exception, KeyboardInterrupt) as e:
        if e != None: 
            print ("Exception is:\n", e)
    client.stop()
    sys.exit(0)