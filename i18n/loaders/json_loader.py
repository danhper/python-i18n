import json

from .loader import Loader, I18nFileLoadError

class JsonLoader(Loader):
    """class to load yaml files"""
    def __init__(self):
        super(JsonLoader, self).__init__()

    def parse_file(self, file_content):
        try:
            return json.load(file_content)
        except ValueError as e:
            raise I18nFileLoadError("Invalid JSON: {0}".format(e.message))
