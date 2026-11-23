import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import i18n
from i18n import config, translations


class TestPreload(unittest.TestCase):
    def setUp(self):
        settings = copy.deepcopy(config.settings)
        contents = copy.deepcopy(translations.container)
        self.addCleanup(lambda: config.settings.update(settings))
        self.addCleanup(lambda: translations.container.update(contents))
        self.addCleanup(translations.container.clear)
        translations.container.clear()
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        config.set("load_path", [str(self.root)])
        config.set("file_format", "json")
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("available_locales", ["en", "fr"])
        config.set("locale", "en")
        config.set("skip_locale_root_data", False)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_loads_nested_namespaces_and_configured_locales_before_first_lookup(self):
        self.write("messages.en.json", {"en": {"hello": "Hello"}})
        self.write("app/messages.fr.json", {"fr": {"hello": "Bonjour"}})
        self.write("ignored.de.json", {"de": {"hello": "Hallo"}})
        i18n.load_all()
        with patch("i18n.resource_loader.search_translation", side_effect=AssertionError):
            self.assertEqual(i18n.t("messages.hello", locale="en"), "Hello")
            self.assertEqual(i18n.t("app.messages.hello", locale="fr"), "Bonjour")
        self.assertNotIn("de", translations.container)
        self.assertEqual(config.get("locale"), "en")

    def test_explicit_locale_and_locale_only_filenames(self):
        config.set("filename_format", "{locale}.{format}")
        self.write("en.json", {"en": {"hello": "Hello"}})
        self.write("fr.json", {"fr": {"hello": "Bonjour"}})
        i18n.load_all(["fr"])
        self.assertEqual(translations.get("hello", "fr"), "Bonjour")
        self.assertNotIn("en", translations.container)

    def test_missing_root_is_reported_at_startup(self):
        config.set("load_path", [str(self.root / "missing")])
        with self.assertRaises(FileNotFoundError):
            i18n.load_all()

    def test_malformed_matching_file_is_reported_at_startup(self):
        (self.root / "messages.en.json").write_text("{", encoding="utf-8")
        with self.assertRaises(i18n.I18nFileLoadError):
            i18n.load_all()
