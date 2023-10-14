from flask import Flask, Response, render_template
import cv2

class EndpointAction(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        result = self.action()
        return result


class Core(object):
    NAME = "3Dasha"

    def __init__(self):
        self.app = Flask(self.NAME)
        self.host = "localhost"
        self.port = 5000
        self.debug = True
        #print(self.list_ports())
        self.camera = cv2.VideoCapture(1)

        self.__add_endpoints()

    def list_ports(self):
        """
        Test the ports and returns a tuple with the available ports and the ones that are working.
        """
        non_working_ports = []
        dev_port = 0
        working_ports = []
        available_ports = []
        while len(non_working_ports) < 6:  # if there are more than 5 non working ports stop the testing.
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                print("Port %s is not working." % dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" % (dev_port, h, w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." % (dev_port, h, w))
                    available_ports.append(dev_port)
            dev_port += 1
        return available_ports, working_ports, non_working_ports

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug, use_reloader=False)

    def gen_frames(self):
        while True:
            success, frame = self.camera.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def __setup_webcam(self):
        return Response(self.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def __add_endpoints(self):
        self.__add_endpoint(endpoint='/', endpoint_name='index', handler=self.__index)
        self.__add_endpoint(endpoint='/webcam', endpoint_name='webcam', handler=self.__setup_webcam)

    @staticmethod
    def __index():
        return render_template("index.html")

    def __add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


if __name__ == "__main__":
    core = Core()
    core.run()

