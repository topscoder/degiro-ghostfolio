import json

class AppConfig:

    def __init__(self) -> None:
        try:
            with open("config/config.json") as config_file:
                self.config_dict = json.load(config_file)
        except:
            print(f"[FATAL] Whoopsie... Can't read config/config.json...")
            exit(1)
        

    def get(self, key=""):
        if key != "":
            return self.config_dict.get(key)
        
        return self.config_dict
