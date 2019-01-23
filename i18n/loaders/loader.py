from .. import config
import io


class I18nFileLoadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Loader(object):
    """Base class to load resources"""
    def __init__(self):
        super(Loader, self).__init__()
        self.memoization_dict = {}

    def _load_file_data(self, filename):
        try:
            with io.open(filename, 'r', encoding=config.get('encoding')) as f:
                return f.read()
        except IOError as e:
            raise I18nFileLoadError("error loading file {0}: {1}".format(filename, e.strerror))

    def load_file(self, filename):
        enable_memoization = config.get('enable_memoization')
        if enable_memoization:
            if filename not in self.memoization_dict:
                self.memoization_dict[filename] = self._load_file_data(filename)
            return self.memoization_dict[filename]
        else:
            return self._load_file_data(filename)

    def parse_file(self, file_content):
        raise NotImplementedError("the method parse_file has not been implemented for class {0}".format(self.__class__.name__))

    def check_data(self, data, root_data):
        return True if root_data is None else root_data in data

    def get_data(self, data, root_data):
        return data if root_data is None else data[root_data]

    def load_resource(self, filename, root_data):
        file_content = self.load_file(filename)
        data = self.parse_file(file_content)
        if not self.check_data(data, root_data):
            raise I18nFileLoadError("error getting data from {0}: {1} not defined".format(filename, root_data))
        return self.get_data(data, root_data)
