import hashlib
import importlib.util
import os.path
import sys

from .loader import I18nFileLoadError, Loader


class PythonLoader(Loader):
    """class to load python files"""

    def __init__(self):
        super().__init__()

    def load_file(self, filename):
        filename = os.path.abspath(filename)
        module_name = "_i18n_config_" + hashlib.sha256(os.fsencode(filename)).hexdigest()
        if module_name in sys.modules:
            return sys.modules[module_name]

        spec = importlib.util.spec_from_file_location(module_name, filename)
        if spec is None or spec.loader is None:
            raise I18nFileLoadError(f"error loading file {filename}")
        module = importlib.util.module_from_spec(spec)
        path = os.path.dirname(filename)
        added_path = path not in sys.path
        if added_path:
            sys.path.append(path)
        sys.modules[module_name] = module
        loaded = False
        try:
            spec.loader.exec_module(module)
            loaded = True
        except (ImportError, OSError) as error:
            raise I18nFileLoadError(f"error loading file {filename}") from error
        finally:
            if not loaded:
                sys.modules.pop(module_name, None)
            if added_path and path in sys.path:
                sys.path.remove(path)
        return module

    def parse_file(self, file_content):
        return file_content

    def check_data(self, data, root_data):
        return hasattr(data, root_data)

    def get_data(self, data, root_data):
        return getattr(data, root_data)
