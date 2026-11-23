import yaml

from .loader import I18nFileLoadError, Loader


class YamlLoader(Loader):
    """class to load yaml files"""

    def __init__(self):
        super().__init__()

    def parse_file(self, file_content):
        try:
            loader = getattr(yaml, "FullLoader", yaml.SafeLoader)
            return yaml.load(file_content, Loader=loader)
        # Keep catching everything: PyYAML can raise more than YAMLError.
        except Exception as e:  # noqa: BLE001
            raise I18nFileLoadError(f"invalid YAML: {e!s}")
