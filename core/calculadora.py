import json

def cargar_configuracion():
    with open("config/normativa_config.json", "r") as f:
        return json.load(f)
