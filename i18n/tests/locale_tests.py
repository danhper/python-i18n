import os
import tempfile
import unittest

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
