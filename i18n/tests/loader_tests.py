# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import os
import os.path
import tempfile

import i18n
from i18n import resource_loader
from i18n.resource_loader import I18nFileLoadError
from i18n.translator import t
from i18n import config
from i18n.config import json_available, yaml_available
from i18n import translations

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3


RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), "resources")


class TestFileLoader(unittest.TestCase):
    def setUp(self):
        resource_loader.loaders = {}
        translations.container = {}
        reload(config)
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations")])
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("encoding", "utf-8")

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
            resource_loader.load_resource(os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "foo")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_yaml_file(self):
        resource_loader.init_yaml_loader()
        data = resource_loader.load_resource(os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.yml"), "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_json_file(self):
        resource_loader.init_json_loader()
        data = resource_loader.load_resource(os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    def test_load_python_file(self):
        resource_loader.init_python_loader()
        data = resource_loader.load_resource(os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.py"), "settings")
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_memoization_with_file(self):
        '''This test creates a temporary file with the help of the
        tempfile library and writes a simple key: value dictionary in it.
        It will then use that file to load the translations and, after having
        enabled memoization, try to access it, causing the file to be (hopefully)
        memoized. It will then _remove_ the temporary file and try to access again,
        asserting that an error is not raised, thus making sure the data is
        actually loaded from memory and not from disk access.'''
        memoization_file_name = 'memoize.en.yml'
        # create the file and write the data in it
        try:
            d = tempfile.TemporaryDirectory()
            tmp_dir_name = d.name
        except AttributeError:
            # we are running python2, use mkdtemp
            tmp_dir_name = tempfile.mkdtemp()
        fd = open('{}/{}'.format(tmp_dir_name, memoization_file_name), 'w')
        fd.write('en:\n  key: value')
        fd.close()
        # create the loader and pass the file to it
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(memoization_file_name, tmp_dir_name)
        # try loading the value to make sure it's working
        self.assertEqual(t('memoize.key'), 'value')
        # now delete the file and directory
        # we are running python2, delete manually
        import shutil
        shutil.rmtree(tmp_dir_name)
        # test the translation again to make sure it's loaded from memory
        self.assertEqual(t('memoize.key'), 'value')


    @unittest.skipUnless(json_available, "json library not available")
    def test_load_file_with_strange_encoding(self):
        resource_loader.init_json_loader()
        config.set("encoding", "euc-jp")
        data = resource_loader.load_resource(os.path.join(RESOURCE_FOLDER, "settings", "eucjp_config.json"), "settings")
        self.assertIn("ほげ", data)
        self.assertEqual("ホゲ", data["ほげ"])

    def test_get_namespace_from_filepath_with_filename(self):
        tests = {
            "foo": "foo.ja.yml",
            "foo.bar": os.path.join("foo", "bar.ja.yml"),
            "foo.bar.baz": os.path.join("foo", "bar", "baz.en.yml"),
        }
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            self.assertEqual(expected, namespace)

    def test_get_namespace_from_filepath_without_filename(self):
        tests = {
            "": "ja.yml",
            "foo": os.path.join("foo", "ja.yml"),
            "foo.bar": os.path.join("foo", "bar", "en.yml"),
        }
        config.set("filename_format", "{locale}.{format}")
        for expected, test_val in tests.items():
            namespace = resource_loader.get_namespace_from_filepath(test_val)
            self.assertEqual(expected, namespace)

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_translation_file(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file("foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations"))

        self.assertTrue(translations.has("foo.normal_key"))
        self.assertTrue(translations.has("foo.parent.nested_key"))

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_plural(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file("foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations"))
        self.assertTrue(translations.has("foo.mail_number"))
        translated_plural = translations.get("foo.mail_number")
        self.assertIsInstance(translated_plural, dict)
        self.assertEqual(translated_plural["zero"], "You do not have any mail.")
        self.assertEqual(translated_plural["one"], "You have a new mail.")
        self.assertEqual(translated_plural["many"], "You have %{count} new mails.")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_search_translation_yaml(self):
        resource_loader.init_yaml_loader()
        config.set("file_format", "yml")
        resource_loader.search_translation("foo.normal_key")
        self.assertTrue(translations.has("foo.normal_key"))

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_json(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")

        resource_loader.search_translation("bar.baz.qux")
        self.assertTrue(translations.has("bar.baz.qux"))

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("filename_format", "{locale}.{format}")
        resource_loader.search_translation("foo")
        self.assertTrue(translations.has("foo"))

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__default_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")])
        config.set("filename_format", "{locale}.{format}")
        config.set('skip_locale_root_data', True)
        config.set("locale", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION")
        self.assertTrue(translations.has("COMMON.VERSION"))
        self.assertEqual(translations.get("COMMON.VERSION"), "version")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__other_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")])
        config.set("filename_format", "{locale}.{format}")
        config.set('skip_locale_root_data', True)
        config.set("locale", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION", locale="pl")
        self.assertTrue(translations.has("COMMON.VERSION", locale="pl"))
        self.assertEqual(translations.get("COMMON.VERSION", locale="pl"), "wersja")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__default_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")])
        config.set("filename_format", "{locale}.{format}")
        config.set('skip_locale_root_data', True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS")
        self.assertTrue(translations.has("TOP_MENU.TOP_BAR.LOGS"))
        self.assertEqual(translations.get("TOP_MENU.TOP_BAR.LOGS"), "Logs")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__other_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")])
        config.set("filename_format", "{locale}.{format}")
        config.set('skip_locale_root_data', True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS", locale="pl")
        self.assertTrue(translations.has("TOP_MENU.TOP_BAR.LOGS", locale="pl"))
        self.assertEqual(translations.get("TOP_MENU.TOP_BAR.LOGS", locale="pl"), "Logi")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
