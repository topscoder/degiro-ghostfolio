import json

class AppConfig:

    def __init__(self) -> None:
        with open("config/config.json") as config_file:
            self.config_dict = json.load(config_file)
        

    def get(self, key=""):
        if key != "":
            return self.config_dict.get(key)
        
        return self.config_dict
