import yaml

from .loader import I18nFileLoadError, Loader


class YamlLoader(Loader):
    """class to load yaml files"""

    def __init__(self):
        super(YamlLoader, self).__init__()

    def parse_file(self, file_content):
        try:
            if hasattr(yaml, "FullLoader"):
                return yaml.load(file_content, Loader=yaml.FullLoader)
            else:
                return yaml.load(file_content)
        except yaml.scanner.ScannerError as e:
            raise I18nFileLoadError("invalid YAML: {0}".format(str(e)))
