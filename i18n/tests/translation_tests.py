import unittest
import os
import os.path

from i18n import resource_loader
from i18n.translator import t
from i18n import config

RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + 'resources' + os.sep

class TestTranslationFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource_loader.init_loaders()
        config.get('load_path').append(os.path.join(RESOURCE_FOLDER, 'translations'))

    def test_basic_translation(self):
        self.assertEqual(t('foo.normal_key'), 'normal_value')
        config.set('file_format', 'json')
        self.assertEqual(t('bar.baz.qux'), 'hoge')
