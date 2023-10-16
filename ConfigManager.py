from os import listdir
from os.path import isfile, join
import json

class ConfigManager:
    def __init__(self, configsPath: str):
        self.configsPath = configsPath
        self.configs = {}

        filenames = [f for f in listdir(self.configsPath) if isfile(join(self.configsPath, f))]
        for filename in filenames:
            with open(f"{self.configsPath}/{filename}") as file:
                converted_file = json.loads(file.read())
                self.configs[filename.split('.')[0]] = converted_file

    def __getitem__(self, key):
        keys = key.split("][")

        value = self.configs
        for k in keys:
            value = value[k]

        return value

    def get_config(self, config_name: str, config_part: str):
        return ConfigManager(self.configsPath)
