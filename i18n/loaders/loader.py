import os

from .. import config


class I18nFileLoadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Loader:
    """Base class to load resources"""

    def __init__(self):
        super().__init__()
        self.memoization_dict = {}

    def _load_file_data(self, filename):
        try:
            if hasattr(filename, "read_text"):
                return filename.read_text(encoding=config.get("encoding"))
            with open(filename, "r", encoding=config.get("encoding")) as f:
                return f.read()
        except OSError as e:
            raise I18nFileLoadError(f"error loading file {filename}: {e.strerror}")

    def load_file(self, filename):
        enable_memoization = config.get("enable_memoization")
        if enable_memoization:
            if isinstance(filename, (str, os.PathLike)):
                cache_key = os.path.abspath(filename)
            else:
                # Package Traversables need not represent filesystem paths.
                cache_key = str(filename)
            if cache_key not in self.memoization_dict:
                self.memoization_dict[cache_key] = self._load_file_data(filename)
            return self.memoization_dict[cache_key]
        else:
            return self._load_file_data(filename)

    def parse_file(self, file_content):
        raise NotImplementedError(
            f"the method parse_file has not been implemented for class {self.__class__.__name__}"
        )

    def check_data(self, data, root_data):
        return True if root_data is None else root_data in data

    def get_data(self, data, root_data):
        return data if root_data is None else data[root_data]

    def load_resource(self, filename, root_data):
        file_content = self.load_file(filename)
        data = self.parse_file(file_content)
        if not self.check_data(data, root_data):
            raise I18nFileLoadError(
                f"error getting data from {filename}: {root_data} not defined"
            )
        return self.get_data(data, root_data)
