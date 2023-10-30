import __main__
import logging
import os
from glob import glob
import functools
import json
import time
import serial

from Common import BackendResponse, CyclicBuffer

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

        self.serial = serial.Serial(self.printer_port, 115200, timeout=2)

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

        self.sequence_time = 1
        self.bed_temperature_history = CyclicBuffer(60, 0)
        self.extruder_temperature_history = CyclicBuffer(60, 0)
        self.move_history = CyclicBuffer(60, {"x": 0, "y": 0, "z": 0})

        self.send_gcode("M118 'Hello'")

    def close_connection(self):
        self.serial.close()

    def monitor(self):

        while True:
            start = time.time()

            temp_raw = self.send_gcode("M105;\n")
            try:
                extruder_temperature = float(temp_raw.decode().split('T:')[1].split(' ')[0])
                bed_temperature = float(temp_raw.decode().split('B:')[1].split(' ')[0])
                self.bed_temperature_history.add_value(bed_temperature)
                self.extruder_temperature_history.add_value(extruder_temperature)
            except Exception:
                pass

            time.sleep(0.2)
            pos_raw = self.send_gcode("M114;\n").decode()
            #print(pos_raw)
            if "ok" not in pos_raw:
                try:
                    lists = pos_raw.split(" ")
                    x_pos = float(lists[0].split(":")[-1])
                    y_pos = float(lists[1].split(":")[-1])
                    z_pos = float(lists[2].split(":")[-1])
                    print(x_pos, y_pos, z_pos)
                    self.move_history.add_value({"x": x_pos, "y": y_pos, "z": z_pos})
                except Exception:
                    pass


            end = time.time()
            time_elapsed = end - start
            time_left = self.sequence_time - time_elapsed
            if time_left > 0:
                time.sleep(time_left)





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
        gcode = f"M140 S{temperature};\n"
        self.send_gcode(gcode)
        print(f"bed temperature set to {temperature}")
        return BackendResponse(success=True, info="bed temperature set!", data={})

    def set_extruder_temperature(self, temperature):
        gcode = f"M104 S{temperature};\n"
        self.send_gcode(gcode)
        print(f"extruder temperature set to {temperature}")
        return BackendResponse(success=True, info="extruder temperature set!", data={})

    def extrude(self, distance):
        gcode = f"G1 E{distance};\n"
        self.send_gcode(gcode)
        print(f"extruded {distance}mm")
        return BackendResponse(success=True, info=f"extruded {distance}mm!", data={})


    def home(self):
        self.send_gcode("G28;\n")
        print("home")
        return BackendResponse(success=True, info=f"home!", data={})

    def move(self, x: float, y: float, z: float):
        gcode = "G91;\n G1"
        if int(x) != 0:
            gcode += f" X{x}"
        if int(y) != 0:
            gcode += f" Y{y}"
        if int(z) != 0:
            gcode += f" Z{z}"
        gcode += ";\n"
        self.send_gcode(gcode)
        print(f"moved by x={x} y={y} z={z}")
        return BackendResponse(success=True, info=f"moved by x={x} y={y} z={z}", data={})

    def send_gcode(self, gcode: str):
        self.serial.write(gcode.encode())
        response = self.serial.readline()
        #print(f"{gcode.strip()} -> {response.decode().strip()}")
        return response

    def init_directory(self):
        if not os.path.isdir(self.files_path):
            print(f"creating directory for printer {self.printer_index}: \"{self.printer_name}\"")
            os.makedirs(self.files_path)

    def fetch_move_history(self):
        history = self.move_history.get_buffer_content()
        return BackendResponse(success=True, info="", data={"points": history, "x_max": self.x_size, "y_max": self.y_size, "z_max": self.z_size})

    def fetch_temperature_history(self):
        bed = list(reversed(self.bed_temperature_history.get_buffer_content()))
        extruder = list(reversed(self.extruder_temperature_history.get_buffer_content()))

        amount = len(bed)
        labels = list(reversed([str(-x) + 'S' for x in range(amount)]))
        return BackendResponse(success=True, info="", data={"bed": bed, "extruder": extruder, "labels": labels})

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
