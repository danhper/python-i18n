# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import os
import os.path
import unittest

from i18n import config, resource_loader, translations
from i18n.translator import t


# Python 3 only: always import reload from importlib
from importlib import reload


RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + "resources" + os.sep


class TestTranslationFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource_loader.init_loaders()
        reload(config)
        config.set("load_path", [os.path.join(RESOURCE_FOLDER, "translations")])
        translations.add("foo.hi", "Hello %{name} !")
        translations.add("foo.hello", "Salut %{name} !", locale="fr")
        translations.add(
            "foo.basic_plural", {"one": "1 elem", "many": "%{count} elems"}
        )
        translations.add(
            "foo.plural",
            {
                "zero": "no mail",
                "one": "1 mail",
                "few": "only %{count} mails",
                "many": "%{count} mails",
            },
        )
        translations.add("foo.bad_plural", {"bar": "foo elems"})

    def setUp(self):
        config.set("error_on_missing_translation", False)
        config.set("error_on_missing_placeholder", False)
        config.set("fallback", "en")
        config.set("locale", "en")

    def test_basic_translation(self):
        self.assertEqual(t("foo.normal_key"), "normal_value")

    def test_missing_translation(self):
        self.assertEqual(t("foo.inexistent"), "foo.inexistent")

    def test_missing_translation_error(self):
        config.set("error_on_missing_translation", True)
        with self.assertRaises(KeyError):
            t("foo.inexistent")

    def test_locale_change(self):
        config.set("locale", "fr")
        self.assertEqual(t("foo.hello", name="Bob"), "Salut Bob !")

    def test_fallback(self):
        config.set("fallback", "fr")
        self.assertEqual(t("foo.hello", name="Bob"), "Salut Bob !")

    def test_fallback_from_resource(self):
        config.set("fallback", "ja")
        self.assertEqual(t("foo.fallback_key"), "フォールバック")

    def test_basic_placeholder(self):
        self.assertEqual(t("foo.hi", name="Bob"), "Hello Bob !")

    def test_missing_placehoder(self):
        self.assertEqual(t("foo.hi"), "Hello %{name} !")

    def test_missing_placeholder_error(self):
        config.set("error_on_missing_placeholder", True)
        with self.assertRaises(KeyError):
            t("foo.hi")

    def test_basic_pluralization(self):
        self.assertEqual(t("foo.basic_plural", count=0), "0 elems")
        self.assertEqual(t("foo.basic_plural", count=1), "1 elem")
        self.assertEqual(t("foo.basic_plural", count=2), "2 elems")

    def test_full_pluralization(self):
        self.assertEqual(t("foo.plural", count=0), "no mail")
        self.assertEqual(t("foo.plural", count=1), "1 mail")
        self.assertEqual(t("foo.plural", count=4), "only 4 mails")
        self.assertEqual(t("foo.plural", count=12), "12 mails")

    def test_bad_pluralization(self):
        config.set("error_on_missing_plural", False)
        self.assertEqual(t("foo.normal_key", count=5), "normal_value")
        config.set("error_on_missing_plural", True)
        with self.assertRaises(KeyError):
            t("foo.bad_plural", count=0)

    def test_default(self):
        self.assertEqual(t("inexistent_key", default="foo"), "foo")

    def test_skip_locale_root_data(self):
        config.set("filename_format", "{locale}.{format}")
        config.set("file_format", "json")
        config.set("locale", "gb")
        config.set("skip_locale_root_data", True)
        resource_loader.init_loaders()
        self.assertEqual(t("foo"), "Lorry")
        config.set("skip_locale_root_data", False)

    def test_skip_locale_root_data_nested_json_dict__default_locale(self):
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.init_json_loader()
        self.assertEqual(t("COMMON.START"), "Start")

    def test_skip_locale_root_data_nested_json_dict__other_locale(self):
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.init_json_loader()
        self.assertEqual(t("COMMON.EXECUTE", locale="pl"), "Wykonaj")
