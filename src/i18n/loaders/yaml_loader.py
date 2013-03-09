import yaml
import sys

class YamlLoader(object):
    def __init__(self):
        super(YamlLoader, self).__init__()

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                return yaml.load(f.read())
        except yaml.scanner.ScannerError:
            sys.stderr.write("Invalid YAML in file {0}".format(filename))
        except IOError:
            pass
