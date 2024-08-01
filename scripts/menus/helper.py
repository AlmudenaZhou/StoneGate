import json
from configparser import ConfigParser
from os import path, getcwd


class Helper:

    @staticmethod
    def get_real_path(path_file):
        real_path = path.realpath(path_file)
        return real_path


class ImportData:
    path_project = path.abspath(getcwd())

    def __init__(self) -> None:
        pass

    @classmethod
    def import_json(cls, data: str):
        with open(str(cls.path_project) + f"/data/{data}.json", "r") as data_json:
            return_data = json.load(data_json)

        return return_data

    @classmethod
    def import_config(cls, section: str = "*", value: str = "", config_path: str = "configurations/config.cfg"):

        return_data = None
        configparser = ConfigParser()
        real_path = Helper.get_real_path(config_path)
        configparser.read(real_path)

        if section != "*":
            if value:
                return_data = configparser.get(section, value)
            else:
                return_data = dict(configparser.items(section))

        return return_data
