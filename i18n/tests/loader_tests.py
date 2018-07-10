# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import os
import os.path

from i18n import resource_loader
from i18n.resource_loader import I18nFileLoadError
from i18n import config
from i18n.config import json_available, yaml_available
from i18n import translations


RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), "resources")


class TestFileLoader(unittest.TestCase):
    def setUp(self):
        resource_loader.loaders = {}
        translations.container = {}
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


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
