"""
    Created by LOTFI Hamza
"""

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

class PirPath(Resource):

    # Default value of pir's payload is: 0
    def __init__(self, name="PirPath", coap_server=None):
        super(PirPath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        
        # default value is 0, no person is detected by the sensor.
        self.payload = "0"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = PirPath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class RfidPath(Resource):

    def __init__(self, name="RfidPath", coap_server=None):
        super(RfidPath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)

        # default value
        self.payload = "{ \"uid\": \"" + "--" + "\",\"status\" :\"" + "--" + "\"}"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = RfidPath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class CamPath(Resource):

    def __init__(self, name="CamPath", coap_server=None):
        super(CamPath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)

        # default value
        self.payload = "{ \"id\": \"" + "1" + "\",\"uid\" :\"" + "TEST-UID" + "\", \"nom\" :\"" + "LOTFI" + "\", \"prenom\" :\"" + "HAMZA" + "\"}"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = CamPath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

class LedOnePath(Resource):

    def __init__(self, name="LedOnePath", coap_server=None):
        super(LedOnePath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "0" # default value is 0, the led is off

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = LedOnePath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

class LedTwoPath(Resource):

    def __init__(self, name="LedTwoPath", coap_server=None):
        super(LedTwoPath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "0" # default value is 0, the led is off

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = LedTwoPath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class LedThreePath(Resource):

    def __init__(self, name="LedThreePath", coap_server=None):
        super(LedThreePath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "0" # default value is 0, the led is off

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        print "post from led three"
        res = LedThreePath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

class CapturePath(Resource):

    def __init__(self, name="CapturePath", coap_server=None):
        super(CapturePath, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "0" # default value is 0, DO NOT Capture.

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = CapturePath()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('esp8266_1_rfid/', RfidPath())
        self.add_resource('esp8266_2_pir/', PirPath())
        self.add_resource('esp8266_3_cam/', CamPath()) # camera path
        self.add_resource('esp8266_1_1/', LedOnePath())
        self.add_resource('esp8266_1_2/', LedTwoPath())
        self.add_resource('esp8266_1_3/', LedThreePath())
        self.add_resource('esp8266_3_capture/', CapturePath())


def main():
    server = CoAPServer("0.0.0.0", 5683)
    try:
        print("server is listen on coap://0.0.0.0:5683")
        server.listen(10)
    except KeyboardInterrupt:
        print ("Server Shutdown")
        server.close()
        print ("Exiting...")

if __name__ == '__main__':
    main()