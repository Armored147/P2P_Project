import yaml
from services.file_service import serve

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

if __name__ == "__main__":
    config = load_config("config/peer1_config.yaml")
    serve(config)
