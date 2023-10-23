from flask import Flask, Response, render_template, request
from typing import List
import cv2
import os

from ConfigManager import ConfigManager
from Printer import Printer
from Common import BackendResponse, response_to_json

class EndpointAction(object):
    def __init__(self, action, name):
        self.action = action
        self.name = name

    def __call__(self, *args, **kwargs):
        if self.name == "printer":
            result = self.action(kwargs["index"])
        else:
            result = self.action()
        return result


class Core(object):
    NAME = "3Dasha"

    def __init__(self):

        self.config_manager = ConfigManager("configs")

        self.app = Flask(self.NAME)
        self.host = self.config_manager["application"]["host"]["value"]
        self.port = self.config_manager["application"]["port"]["value"]
        self.debug = self.config_manager["application"]["debug"]["value"]

        self.printers = self.__add_printers()

        print(self.list_ports())  
        self.camera = cv2.VideoCapture(0)

        self.__add_endpoints()

    def __add_printers(self) -> List[Printer]:
        """
        this method will iterate trough printers.json config and fetch all the data about printers into list
        :return: List[Printer]
        """
        printers = []
        for index in range(len(self.config_manager["printers"])):
            printer_config = list(self.config_manager["printers"].values())[index]
            printer = Printer(index, printer_config)
            printers.append(printer)
        return printers

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
        self.__add_endpoint(endpoint='/printer/<int:index>', endpoint_name='printer', handler=self.__printer)
        self.__add_endpoint(endpoint='/createNewDirectory', endpoint_name='createNewDirectory', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/setBedTemperature', endpoint_name='setBedTemperature', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/setExtruderTemperature', endpoint_name='setExtruderTemperature', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/webcam', endpoint_name='webcam', handler=self.__setup_webcam)

    @staticmethod
    def __index():
        return render_template("index.html")

    def __printer_proxy(self):

        if 'printer' not in request.values:
            return {"success": False, "reason": "bad request args"}

        index = int(request.values["printer"])

        if index < 0 or index >= len(self.printers):
            return {"success": False, "reason": "printer does not exist"}

        printer = self.printers[index]
        if request.endpoint == "createNewDirectory":
            directory_name = request.values["directoryName"]
            directory_path = request.values["directoryPath"]
            result = printer.create_new_directory(directory_name=directory_name, directory_path=directory_path)
            return response_to_json(result)
        elif request.endpoint == "setBedTemperature":
            temperature = request.values["temperature"]
            result = printer.set_bed_temperature(temperature=temperature)
            return response_to_json(result)
        elif request.endpoint == "setExtruderTemperature":
            temperature = request.values["temperature"]
            result = printer.set_extruder_temperature(temperature=temperature)
            return response_to_json(result)

        return {"success": False, "reason": "endpoint does not exist"}


    def __printer(self, index: int):
        print(f"printer {index}")
        if index < 0 or index >= len(self.printers):
            return "printer not found"
        printer = self.printers[index]
        return render_template("printer.html", printer=printer)

    def __add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler, endpoint_name))


if __name__ == "__main__":
    core = Core()
    core.run()

