import __main__
import os
from glob import glob
import functools
import json

from Common import BackendResponse


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

        #  printing status  #
        self.isPrinting = False
        self.isActive = False
        self.isIdle = True
        self.printer_status = self.get_printer_status()
        #####################

        #  print status variables  #
        self.printed_file = ""
        self.timelapse_time = 0
        self.print_time = 0
        self.print_time_left = 0
        self.printed_kb = "--/--kb"
        self.printed_percentage = 0
        ############################

        self.is_file_uploaded = False
        self.uploaded_file_path = ""

        self.project_path = '/'.join(__main__.__file__.split("/")[:-1])
        self.files_path = f"{self.project_path}/files/{self.printer_index}/"
        self.init_directory()

        self.directory_tree = self.fetch_directories(self.files_path)
        self.directory_tree_js = json.dumps(self.directory_tree)

        json_formatted_str = json.dumps(self.directory_tree, indent=3)
        print(json_formatted_str)

    def create_new_directory(self, directory_name, directory_path) -> BackendResponse:
        global_path = (self.files_path + directory_path).replace("//", "/")
        path = global_path + directory_name
        if os.path.isdir(path):
            return BackendResponse(success=False, info="directory already exist", data={})

        if os.path.isdir(global_path):
            os.makedirs(path)
            return BackendResponse(success=True, info="successfully created directory!", data={})

        return BackendResponse(success=False, info="path does not exist", data={})

    def set_bed_temperature(self, temperature):
        # TODO: send gcode bed temperature
        print(f"bed temperature set to {temperature}")
        return BackendResponse(success=True, info="bed temperature set!", data={})

    def set_extruder_temperature(self, temperature):
        # TODO: send gcode extruder temperature
        print(f"extruder temperature set to {temperature}")
        return BackendResponse(success=True, info="extruder temperature set!", data={})

    def extrude(self, distance):
        # TODO: send gcode extrude
        print(f"extruded {distance}mm")
        return BackendResponse(success=True, info=f"extruded {distance}mm!", data={})

    def move(self, x, y, z):
        # TODO: send gcode move
        print(f"moved by x={x} y={y} z={z}")
        return BackendResponse(success=True, info=f"moved by x={x} y={y} z={z}", data={})

    def init_directory(self):
        if not os.path.isdir(self.files_path):
            print(f"creating directory for printer {self.printer_index}: \"{self.printer_name}\"")
            os.makedirs(self.files_path)

    def fetch_printer_info(self):
        data = {"name": self.printer_name,
                "index": self.printer_index,
                "port": self.printer_port,
                "status": self.get_printer_status()
                }
        return BackendResponse(success=True, info=f"", data=data)

    def fetch_print_status(self):
        if self.isPrinting:
            data = {"printed_file": self.printed_file,
                    "timelapse_time": self.timelapse_time,
                    "print_time": self.print_time,
                    "print_time_left": self.print_time_left,
                    "printed_kb": self.printed_kb,
                    "printed_percentage": self.printed_percentage,
                    "is_file_uploaded": self.is_file_uploaded,
                    "is_printing": False
                    }
        else:
            data = {"printed_file": "--",
                    "timelapse_time": "--",
                    "print_time": "--:--:--",
                    "print_time_left": "--:--:--",
                    "printed_kb": "--/--",
                    "printed_percentage": 0,
                    "is_file_uploaded": self.is_file_uploaded,
                    "is_printing": False}

        return BackendResponse(success=True, info=f"", data=data)

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
