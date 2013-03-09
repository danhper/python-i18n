import os.path
import config
import sys

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

def load_python(filename):
    path, name = os.path.split(filename)
    module_name, ext = os.path.splitext(name)
    if path not in sys.path:
        sys.path.append(path)
    try:
        translations = __import__(module_name)
        if not hasattr(translations, config.current_locale()):
            raise I18nFileLoadError("Error loading file {0}: {1} not defined".format(filename), config.current_locale())
        return getattr(translations, config.current_locale())
    except ImportError:
        raise I18nFileLoadError("Error loading file {0}".format(filename))

register_loader(load_python, ["py"])

try:
    import yaml

    def load_yaml(filename):
        try:
            translations = yaml.load(load_file(filename))
            if config.current_locale() not in translations:
                raise I18nFileLoadError("Error loading file {0}: {1} not defined".format(filename), config.current_locale())
            return translations[config.current_locale()]
        except yaml.scanner.ScannerError:
            raise I18nFileLoadError("Invalid YAML in file {0}.".format(filename))

    register_loader(load_yaml, ["yml", "yaml"])
except ImportError:
    pass

try:
    import json

    def load_json(filename):
        try:
            translations = json.loads(load_file(filename))
            if config.current_locale() not in translations:
                raise I18nFileLoadError("Error loading file {0}: {1} not defined".format(filename), config.current_locale())
            return translations[config.current_locale()]
        except ValueError:
            raise I18nFileLoadError("Invalid JSON in file {0}.".format(filename))

    register_loader(load_json, ["json"])
except ImportError:
    pass
