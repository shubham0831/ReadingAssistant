import logging as log
import json
from UniqueDict import UniqueDict
import os

class Config:
    def __init__(self):
        self.filePath = os.path.join(os.getcwd(), "config.json")
        self.config = self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.filePath, 'r') as configFile:
                return UniqueDict.fromDict(json.load(configFile))
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.filePath} not found")
        
    def get(self, key):
        return self.config[key]
