import os.path

__all__ = ["register_loader", "I18nFileLoadError"]

loaders = {}

class I18nFileLoadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def register_loader(loader_function, supported_extensions):
    for extension in supported_extensions:
        loaders[extension] = loader_function

def load_resource(filename):
    extension = os.path.splitext(filename)[1:]
    if extension not in loaders:
        raise I18nFileLoadError("No loader available for extension {0}".format(extension))
    return loaders[extension](filename)

def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except IOError as e:
        raise I18nFileLoadError("Error while opening file {0}: {1}".format(filename, e.message))

try:
    import yaml

    def load_yaml(filename):
        try:
            return yaml.load(load_file(filename))
        except yaml.scanner.ScannerError:
            raise I18nFileLoadError("Invalid YAML in file {0}.".format(filename))

    register_loader(load_yaml, ["yml", "yaml"])
except ImportError:
    pass

try:
    import json

    def load_json(filename):
        try:
            return json.loads(load_file(filename))
        except ValueError:
            raise I18nFileLoadError("Invalid JSON in file {0}.".format(filename))

    register_loader(load_json, ["json"])
except ImportError:
    pass
