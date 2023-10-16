import __main__
import os
from glob import glob
import functools
import json
class Printer:
    def __init__(self, printer_index: int, printer_config: dict):
        self.printer_index = printer_index
        self.printer_name = printer_config["printerSettings"]["name"]["value"]
        self.printer_port = printer_config["printerSettings"]["port"]["value"]

        self.camera_present = printer_config["cameraSettings"]["isUsed"]["value"]
        self.camera_port = printer_config["cameraSettings"]["port"]["value"]

        self.x_size = printer_config["movementSettings"]["xSize"]["value"]
        self.y_size = printer_config["movementSettings"]["ySize"]["value"]
        self.z_size = printer_config["movementSettings"]["zSize"]["value"]

        self.extruder_min_temperature = printer_config["extruderSettings"]["extruderMinTemperature"]["value"]
        self.extruder_max_temperature = printer_config["extruderSettings"]["extruderMaxTemperature"]["value"]
        self.extruder_default_temperature = printer_config["extruderSettings"]["extruderDefaultTemperature"]["value"]

        self.extruder_min_temperature = printer_config["bedSettings"]["bedMinTemperature"]["value"]
        self.extruder_max_temperature = printer_config["bedSettings"]["bedMaxTemperature"]["value"]
        self.extruder_default_temperature = printer_config["bedSettings"]["bedDefaultTemperature"]["value"]

        self.isPrinting = False
        self.isActive = False
        self.isIdle = True
        self.printer_status = self.get_printer_status()

        self.project_path = '/'.join(__main__.__file__.split("/")[:-1])
        self.files_path = f"{self.project_path}/files/{self.printer_index}/"
        self.init_directory()

        self.directory_tree = self.fetch_directories(self.files_path)
        self.directory_tree_js = json.dumps(self.directory_tree)

        json_formatted_str = json.dumps(self.directory_tree, indent=3)
        print(json_formatted_str)

    def init_directory(self):
        if not os.path.isdir(self.files_path ):
            print(f"creating directory for printer {self.printer_index}: \"{self.printer_name}\"")
            os.makedirs(self.files_path )

    def fetch_directories(self, root_directory):
        """
        Create a dictionary that represents the folder structure of directory.
        
        :param root_directory: root directory path
        :return: directory structure in nested dictionary
        """

        dir = {}
        root_directory = root_directory.rstrip(os.sep)
        start = root_directory.rfind(os.sep) + 1
        for path, dirs, files in os.walk(root_directory):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = functools.reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
        return dir[str(self.printer_index)]

    def set_printer_status(self, status: str):
        states = ["idle", "active", "printing"]
        if status not in states:
            raise Exception(f"printer state should be on of these: {states}")

        if status == "idle":
            self.isIdle = True
            self.isActive = False
            self.isPrinting = False
        elif status == "active":
            self.isIdle = False
            self.isActive = True
            self.isPrinting = False
        elif status == "printing":
            self.isIdle = False
            self.isActive = False
            self.isPrinting = True

    def get_printer_status(self) -> str:
        if self.isIdle:
            return "idle"
        elif self.isActive:
            return "active"
        elif self.isPrinting:
            return "printing"
        else:
            raise Exception("printer is not in any state!")

    def get_info(self) -> str:
        info = ""
        info += f"Printer Name: {self.printer_name}\n"
        info += f"Printer Port: {self.printer_port}\n"
        return info
