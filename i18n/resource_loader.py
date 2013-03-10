import os.path

from .loaders.loader import I18nFileLoadError

loaders = {}

def register_loader(loader_class, supported_extensions):
    if not hasattr(loader_class, "load_resource"):
        raise ValueError("loader class should have a 'load_resource' method")

    for extension in supported_extensions:
        loaders[extension] = loader_class()

def load_resource(filename, root_data):
    extension = os.path.splitext(filename)[1][1:]
    if extension not in loaders:
        raise I18nFileLoadError("no loader available for extension {0}".format(extension))
    return getattr(loaders[extension], "load_resource")(filename, root_data)

def init_python_loader():
    from .loaders.python_loader import PythonLoader
    register_loader(PythonLoader, ["py"])

def init_yaml_loader():
    try:
        from .loaders.yaml_loader import YamlLoader
        register_loader(YamlLoader, ["yml", "yaml"])
    except ImportError:
        pass

def init_json_loader():
    try:
        from .loaders.json_loader import JsonLoader
        register_loader(JsonLoader, ["json"])
    except ImportError:
        pass
