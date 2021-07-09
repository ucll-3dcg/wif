from pathlib import Path
import os
import os.path
import json


CONFIG_FILENAME = 'wifcfg.json'


configuration = {
    'raytracer': None,
    'block_size': 500000,
}


def get_configuration_path():
    home = Path.home()
    return home / CONFIG_FILENAME


def init():
    path = get_configuration_path()
    if os.path.exists(path):
        _load_configuration()
    else:
        _create_configuration_file()


def write():
    path = get_configuration_path()
    with open(path, 'w') as file:
        json.dump(configuration, file)


def _load_configuration():
    global configuration
    path = get_configuration_path()
    with open(path) as file:
        configuration = json.load(file)


def _create_configuration_file():
    global configuration
    path = get_configuration_path()
    with open(path, 'w') as file:
        json.dump(configuration, file)


def reset_configuration():
    path = get_configuration_path()
    os.remove(path)
