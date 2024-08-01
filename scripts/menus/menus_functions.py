from scripts.menus.helper import ImportData


class MenusFunctions:

    function_mapping = ImportData.import_config(config_path="maps.cfg")

    @staticmethod
    def test_function():
        pass
