import json
import os
import tempfile
import unittest

import i18n
from i18n import add_translation, config, resource_loader, translations
from i18n.translator import t


class TestTranslationLocale(unittest.TestCase):
    def setUp(self):
        self.addCleanup(setattr, config, "settings", config.settings.copy())
        self.addCleanup(setattr, translations, "container", translations.container)
        translations.container = {}

    def test_add_translation_uses_current_locale(self):
        config.set("locale", "fr")
        add_translation("greeting", "Bonjour")
        self.assertTrue(translations.has("greeting", locale="fr"))
        self.assertFalse(translations.has("greeting", locale="en"))
        self.assertEqual(t("greeting", locale="fr"), "Bonjour")

    def test_public_set_changes_the_translation_locale(self):
        i18n.add_translation("greeting", "Hello", locale="en")
        i18n.add_translation("greeting", "Bonjour", locale="fr")
        i18n.set("locale", "fr")
        self.assertEqual(i18n.t("greeting"), "Bonjour")
        i18n.set("locale", "en")
        self.assertEqual(i18n.t("greeting"), "Hello")

    def test_public_get_reads_current_configuration(self):
        for locale in ("fr", "en"):
            with self.subTest(locale=locale):
                config.set("locale", locale)
                self.assertEqual(i18n.get("locale"), locale)

    def test_public_load_paths_follow_configuration_replacement(self):
        for setter in (i18n.set, config.set):
            for name in ("load_path", "load_package_path"):
                with self.subTest(setter=setter, name=name):
                    replacement = []
                    setter(name, replacement)
                    self.assertIs(getattr(i18n, name), replacement)
                    getattr(i18n, name).append("configured")
                    self.assertEqual(config.get(name), ["configured"])

    def test_public_load_paths_follow_loaded_configuration(self):
        resource_loader.init_json_loader()
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "settings.json")
            with open(filename, "w", encoding="utf-8") as stream:
                json.dump(
                    {"settings": {"load_path": [], "load_package_path": []}}, stream
                )
            i18n.load_config(filename)
            for name in ("load_path", "load_package_path"):
                self.assertIs(getattr(i18n, name), config.get(name))

    def test_public_load_path_append_reaches_the_translation_loader(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("namespace_delimiter", ".")
        config.set("skip_locale_root_data", False)
        config.set("load_path", [])
        config.set("load_package_path", [])
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "live.en.json")
            with open(filename, "w", encoding="utf-8") as stream:
                json.dump({"en": {"hello": "Hello from current path"}}, stream)
            original_path = i18n.load_path[:]
            self.addCleanup(i18n.load_path.__setitem__, slice(None), original_path)
            i18n.load_path.append(directory)
            self.assertEqual(
                i18n.t("live.hello", locale="en"), "Hello from current path"
            )

    def test_public_load_paths_remain_discoverable_and_importable(self):
        config.set("load_path", [])
        config.set("load_package_path", [])
        imported = {}
        exec("from i18n import *", imported)  # noqa: S102
        for name in ("load_path", "load_package_path"):
            self.assertIn(name, dir(i18n))
            self.assertIs(imported[name], config.get(name))
        with self.assertRaises(AttributeError):
            _ = i18n.unknown_configuration_attribute

    def test_lookup_defaults_follow_locale_changes(self):
        add_translation("greeting", "Hello", locale="en")
        add_translation("greeting", "Bonjour", locale="fr")
        add_translation("french_only", "Oui", locale="fr")
        for locale, expected in (("fr", "Bonjour"), ("en", "Hello")):
            with self.subTest(locale=locale):
                config.set("locale", locale)
                self.assertEqual(translations.get("greeting"), expected)
                self.assertEqual(translations.has("french_only"), locale == "fr")

    def test_explicit_locale_takes_precedence(self):
        config.set("locale", "fr")
        add_translation("greeting", "Hello", locale="en")
        self.assertEqual(translations.get("greeting", locale="en"), "Hello")
        self.assertFalse(translations.has("greeting", locale="fr"))

    def test_resource_loaders_use_current_locale(self):
        resource_loader.init_json_loader()
        config.set("locale", "ja")
        config.set("file_format", "json")
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("skip_locale_root_data", False)
        with tempfile.TemporaryDirectory() as directory:
            with open(
                os.path.join(directory, "current.ja.json"), "w", encoding="utf-8"
            ) as resource:
                resource.write('{"ja": {"greeting": "Konnichiwa"}}')
            config.set("load_path", [directory])
            loaders = (
                lambda: resource_loader.load_translation_file(
                    "current.ja.json", directory
                ),
                lambda: resource_loader.load_directory(directory),
                lambda: resource_loader.search_translation("current.greeting"),
                lambda: resource_loader.recursive_search_dir(
                    ["current"], "", directory
                ),
            )
            for index, loader in enumerate(loaders):
                with self.subTest(loader=index):
                    translations.container = {}
                    loader()
                    self.assertEqual(
                        translations.get("current.greeting", locale="ja"), "Konnichiwa"
                    )
                    self.assertFalse(translations.has("current.greeting", locale="en"))
