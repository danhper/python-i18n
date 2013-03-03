import yaml

from loader import Loader

class YMLLoader(Loader):
    """docstring for YMLLoader"""
    def __init__(self, arg):
        super(YMLLoader, self).__init__()
        self.arg = arg

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except IOError as e:
            pass
