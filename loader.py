import json
import sys
import logging

class ConfigLoad():
    def __init__(self, config_file):
        self.config_file = config_file
    def conf_load(self):
        try:
            with open(self.config_file) as f: # считываем конфиг
                return json.load(f)
        except FileNotFoundError:
            logging.info("Файл не найден")
            sys.exit(1)