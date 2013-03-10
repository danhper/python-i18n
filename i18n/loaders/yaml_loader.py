import yaml

from .loader import Loader, I18nFileLoadError

class YamlLoader(Loader):
    """class to load yaml files"""
    def __init__(self):
        super(YamlLoader, self).__init__()

    def parse_file(self, file_content):
        try:
            return yaml.loads(file_content)
        except yaml.scanner.ScannerError as e:
            raise I18nFileLoadError("Invalid YAML: {0}".format(e.strerror))
