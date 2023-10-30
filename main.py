import serial.serialutil
from flask import Flask, Response, render_template, request
from typing import List
from threading import Thread
import cv2
import os
import logging

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
        elif self.name == "webcam":
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

        self.threads = []

        for printer in self.printers:
            self.threads.append(Thread(target=printer.monitor))

        for thread in self.threads:
            thread.start()

        self.__add_endpoints()

    def __add_printers(self) -> List[Printer]:
        """
        this method will iterate trough printers.json config and fetch all the data about printers into list
        :return: List[Printer]
        """
        printers = []
        for index in range(len(self.config_manager["printers"])):
            printer_config = list(self.config_manager["printers"].values())[index]
            try:
                printer = Printer(index, printer_config)
                printers.append(printer)
            except serial.serialutil.SerialException as e:
                name = printer_config["printerSettings"]["name"]["value"]
                port = printer_config["printerSettings"]["port"]["value"]
                logging.getLogger().error(f'could not add printer "{name}" on port "{port}"')
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

    def gen_frames(self, index: int):
        camera_port = self.printers[index].camera_port
        cam = cv2.VideoCapture(camera_port)
        while True:
            success, frame = cam.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def __setup_webcam(self, index: int):
        return Response(self.gen_frames(index), mimetype='multipart/x-mixed-replace; boundary=frame')

    def __add_endpoints(self):
        self.__add_endpoint(endpoint='/', endpoint_name='index', handler=self.__index)
        self.__add_endpoint(endpoint='/printer/<int:index>', endpoint_name='printer', handler=self.__printer)
        self.__add_endpoint(endpoint='/createNewDirectory', endpoint_name='createNewDirectory', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/setBedTemperature', endpoint_name='setBedTemperature', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/setExtruderTemperature', endpoint_name='setExtruderTemperature', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/extrude', endpoint_name='extrude', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/move', endpoint_name='move', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/fetchPrintStatus', endpoint_name='fetchPrintStatus', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/fetchPrinterInfo', endpoint_name='fetchPrinterInfo', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/fetchMoveHistory', endpoint_name='fetchMoveHistory', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/fetchTemperatureHistory', endpoint_name='fetchTemperatureHistory', handler=self.__printer_proxy)
        self.__add_endpoint(endpoint='/webcam/<int:index>', endpoint_name='webcam', handler=self.__setup_webcam)

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
        elif request.endpoint == "extrude":
            distance = request.values["distance"]
            result = printer.extrude(distance=distance)
            return response_to_json(result)
        elif request.endpoint == "move":
            x = request.values["x"]
            y = request.values["y"]
            z = request.values["z"]
            result = printer.move(x=x, y=y, z=z)
            return response_to_json(result)
        elif request.endpoint == "fetchPrintStatus":
            result = printer.fetch_print_status()
            return response_to_json(result)
        elif request.endpoint == "fetchPrinterInfo":
            result = printer.fetch_printer_info()
            return response_to_json(result)
        elif request.endpoint == "fetchMoveHistory":
            result = printer.fetch_move_history()
            return response_to_json(result)
        elif request.endpoint == "fetchTemperatureHistory":
            result = printer.fetch_temperature_history()
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
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    core = Core()
    core.run()

