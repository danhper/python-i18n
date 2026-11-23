import json

from .loader import I18nFileLoadError, Loader


class JsonLoader(Loader):
    """class to load yaml files"""

    def __init__(self):
        super().__init__()

    def parse_file(self, file_content):
        try:
            return json.loads(file_content)
        except ValueError as e:
            raise I18nFileLoadError(f"invalid JSON: {e!s}")
