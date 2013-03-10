import unittest
import os
import os.path

from i18n import resource_loader
from i18n.resource_loader import I18nFileLoadError
from i18n.config import json_available, yaml_available

RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + 'resources' + os.sep

class TestTranslationFormat(unittest.TestCase):
    pass
