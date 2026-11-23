# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import os
import os.path
import unittest

# Python 3 only: always import reload from importlib
from importlib import reload

from i18n import config, resource_loader, translations
from i18n.translator import t

RESOURCE_FOLDER = os.path.dirname(__file__) + os.sep + "resources" + os.sep


class TestTranslationFormat(unittest.TestCase):
    def setUp(self):
        self.addCleanup(setattr, config, "settings", config.settings)
        self.addCleanup(setattr, resource_loader, "loaders", resource_loader.loaders)
        self.addCleanup(setattr, translations, "container", translations.container)
        reload(config)
        resource_loader.loaders = {}
        translations.container = {}
        resource_loader.init_loaders()
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

    def test_configured_placeholder_delimiter(self):
        self.addCleanup(config.set, "placeholder_delimiter", "%")
        for delimiter in ("#", "$", ".", "@@", "%"):
            with self.subTest(delimiter=delimiter):
                config.set("placeholder_delimiter", delimiter)
                translations.add("custom", "Hello " + delimiter + "{name} !")
                self.assertEqual(t("custom", name="Bob"), "Hello Bob !")

    def test_configured_delimiter_preserves_literal_percent(self):
        self.addCleanup(config.set, "placeholder_delimiter", "%")
        config.set("placeholder_delimiter", "#")
        config.set("error_on_missing_placeholder", True)
        translations.add("custom", "10 % and #{name}, ##")
        self.assertEqual(t("custom", name="Bob"), "10 % and Bob, #")

    def test_configured_delimiter_missing_and_invalid_placeholders(self):
        self.addCleanup(config.set, "placeholder_delimiter", "%")
        config.set("placeholder_delimiter", "#")
        translations.add("custom", "Hello #{name}")
        self.assertEqual(t("custom"), "Hello #{name}")
        config.set("error_on_missing_placeholder", True)
        with self.assertRaises(KeyError):
            t("custom")
        translations.add("custom", "10 # !")
        with self.assertRaises(ValueError):
            t("custom")

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

    def test_list(self):
        months = t("foo.months")
        self.assertEqual(len(months), 12)
        self.assertEqual(months[1], "February")

    def test_list_placeholders(self):
        self.assertEqual(t("foo.welcome", user="Bob"), ["Hi Bob", "Welcome to Bob"])

    def test_list_custom_placeholder_delimiter(self):
        config.set("placeholder_delimiter", "#")
        translations.add("foo.custom_list", ["Hi #{user}", "%{user}"])
        self.assertEqual(t("foo.custom_list", user="Bob"), ["Hi Bob", "%{user}"])

    def test_list_pluralization(self):
        self.assertEqual(
            t("foo.welcome_plural", count=1, user="Bob"),
            ["A new user just joined!", "Hello Bob"],
        )
        self.assertEqual(
            t("foo.welcome_plural", count=3, user="Bob"),
            ["3 new users just joined!", "Hello Bob"],
        )

    def test_list_strings_with_count_and_missing_plural_error(self):
        config.set("error_on_missing_plural", True)
        self.assertEqual(
            t("foo.welcome", count=2, user="Bob"), ["Hi Bob", "Welcome to Bob"]
        )

    def test_list_dict_without_count_is_unchanged(self):
        self.assertEqual(
            t("foo.welcome_plural", user="Bob")[0],
            {
                "one": "A new user just joined!",
                "many": "%{count} new users just joined!",
            },
        )

    def test_list_mixed_values(self):
        self.assertEqual(t("foo.mixed", user="Bob"), [42, ["nested Bob", "deep"], None])

    def test_list_fallback(self):
        config.set("locale", "fr")
        config.set("fallback", "en")
        self.assertEqual(t("foo.welcome", user="Bob")[0], "Hi Bob")
