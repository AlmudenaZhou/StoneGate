from inspect import getmembers, ismethod

from importlib import import_module

from scripts.menus.helper import ImportData


class GetModule:

    FUNCTIONS = ImportData.import_config(config_path='data/maps.cfg', section='MENUS')

    def __init__(self) -> None:
        pass

    @staticmethod
    def import_class(package_name, module_name, class_name):

        # To check classes
        # clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

        strategy = False

        try:
            imported_module = import_module(f'{package_name}.{module_name}')
            print(f'Imported module: {imported_module}')

            module_class = getattr(imported_module, class_name)
            print(f'Imported class: {module_class}')

            return module_class

        except Exception as e:
            print("Unable to get the filter")
            print(str(e))

        return strategy


class GetFunction(GetModule):

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def import_menus_class(cls):

        path = "scripts"
        function_module = "menus_functions"
        class_name = "MenusFunctions"

        function_class = cls.import_class(path, function_module, class_name)
        print(f'Function class acquired: {function_class}')

        return function_class

    @classmethod
    def get_function(cls, function_class, function_name: str = "main"):

        function_name = cls.FUNCTIONS[function_name]
        print(f'Mapping: {cls.PARAMETER_CALCULATORS}')

        module = getattr(function_class, function_name)
        print(f'Filter module acquired: {module}')
        return module

    @classmethod
    def get_modules(cls, imported_class, module_names: list = None):

        modules = getmembers(imported_class, predicate=ismethod)
        if module_names:
            for module in modules:
                if not (module[0] in module_names):
                    modules.remove(module)

        else:
            modules.pop(0)

        return modules