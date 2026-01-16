import yaml

from .loader import I18nFileLoadError, Loader


class YamlLoader(Loader):
    """class to load yaml files"""

    def __init__(self):
        super(YamlLoader, self).__init__()

    def parse_file(self, file_content):
        try:
            loader = getattr(yaml, "FullLoader", yaml.SafeLoader)
            return yaml.load(file_content, Loader=loader)
        except Exception as e:
            raise I18nFileLoadError("invalid YAML: {0}".format(str(e)))
