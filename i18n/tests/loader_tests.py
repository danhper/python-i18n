import unittest
import os
import os.path

from i18n import resource_loader
from i18n.resource_loader import I18nFileLoadError
from i18n import config
from i18n.config import json_available, yaml_available


RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + 'resources' + os.sep

class TestFileLoader(unittest.TestCase):
    def setUp(self):
        resource_loader.loaders = {}

    def test_load_unavailable_extension(self):
        with self.assertRaisesRegexp(I18nFileLoadError, "no loader .*"):
            resource_loader.load_resource("foo.bar", "baz")

    def test_register_wrong_loader(self):
        class WrongLoader(object):
            pass
        with self.assertRaises(ValueError):
            resource_loader.register_loader(WrongLoader, [])

    def test_register_python_loader(self):
        resource_loader.init_python_loader()
        with self.assertRaisesRegexp(I18nFileLoadError, "error loading file .*"):
            resource_loader.load_resource("foo.py", "bar")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_register_yaml_loader(self):
        resource_loader.init_yaml_loader()
        with self.assertRaisesRegexp(I18nFileLoadError, "error loading file .*"):
            resource_loader.load_resource("foo.yml", "bar")

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_wrong_json_file(self):
        resource_loader.init_json_loader()
        with self.assertRaisesRegexp(I18nFileLoadError, "error getting data .*"):
            resource_loader.load_resource(RESOURCE_FOLDER + "dummy_config.json", "foo")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_yaml_file(self):
        resource_loader.init_yaml_loader()
        data = resource_loader.load_resource(RESOURCE_FOLDER + "dummy_config.yml", "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data['foo'])

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_json_file(self):
        resource_loader.init_json_loader()
        data = resource_loader.load_resource(RESOURCE_FOLDER + "dummy_config.json", "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data['foo'])

    def test_load_python_file(self):
        resource_loader.init_python_loader()
        data = resource_loader.load_resource(RESOURCE_FOLDER + "dummy_config.py", "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data['foo'])

    def test_load_file_with_strange_encoding(self):
        resource_loader.init_json_loader()
        config.set("encoding", "euc-jp")
        data = resource_loader.load_resource(RESOURCE_FOLDER + "eucjp_config.json", "settings")
        self.assertIn("ほげ", data)
        self.assertEqual("ホゲ", data['ほげ'])

    def test_get_namespace_from_filepath_with_filename(self):
        tests = {
            'foo': 'foo.ja.yml',
            'foo.bar': '/foo/bar.ja.yml',
            'foo.bar.baz': 'foo/bar/baz.en.yml',
        }
        config.set('file_name_format', '{namespace}.{locale}.{format}')
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            self.assertEqual(expected, namespace)

    def test_get_namespace_from_filepath_without_filename(self):
        tests = {
            '': 'ja.yml',
            'foo': '/foo/ja.yml',
            'foo.bar': 'foo/bar/en.yml',
        }
        config.set('file_name_format', '{locale}.{format}')
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            self.assertEqual(expected, namespace)


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
