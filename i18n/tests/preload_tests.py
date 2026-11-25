import copy
import json
import sys
import tempfile
import unittest
import zipfile
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
        config.set("load_package_path", [])
        config.set("file_format", "json")
        config.set("filename_format", "{namespace}.{locale}.{format}")
        config.set("available_locales", ["en", "fr"])
        config.set("locale", "en")
        config.set("skip_locale_root_data", False)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def package(self, name, resources, zipped=True):
        contents = {"__init__.py": b""}
        for filename, value in resources.items():
            text = (
                value
                if isinstance(value, str)
                else json.dumps(value, ensure_ascii=False)
            )
            contents[filename] = text.encode(config.get("encoding"))
        if zipped:
            location = str(self.root / (name + ".zip"))
            with zipfile.ZipFile(location, "w") as archive:
                for filename, content in contents.items():
                    archive.writestr(name + "/" + filename, content)
        else:
            location = str(self.root)
            for filename, content in contents.items():
                path = self.root / name / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
        sys.path.insert(0, location)
        self.addCleanup(sys.path.remove, location)
        self.addCleanup(sys.path_importer_cache.pop, location, None)
        self.addCleanup(sys.modules.pop, name, None)
        return name

    def test_loads_nested_namespaces_and_configured_locales_before_first_lookup(self):
        self.write("messages.en.json", {"en": {"hello": "Hello"}})
        self.write("app/messages.fr.json", {"fr": {"hello": "Bonjour"}})
        self.write("ignored.de.json", {"de": {"hello": "Hallo"}})
        i18n.load_all()
        with patch(
            "i18n.resource_loader.search_translation", side_effect=AssertionError
        ):
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

    def test_preloads_package_locales_and_directory_namespaces(self):
        config.set("load_path", [])
        for zipped in (False, True):
            with self.subTest(zipped=zipped):
                package = self.package(
                    "preload_zip_resources"
                    if zipped
                    else "preload_directory_resources",
                    {
                        "messages.en.json": {"en": {"hello": "Hello"}},
                        "nested/messages.fr.json": {"fr": {"hello": "Bonjour"}},
                        "ignored.de.json": {"de": {"hello": "Hallo"}},
                    },
                    zipped=zipped,
                )
                config.set("load_package_path", [package])
                translations.container.clear()
                i18n.load_all()
                with patch(
                    "i18n.resource_loader.search_translation",
                    side_effect=AssertionError,
                ):
                    self.assertEqual(i18n.t("messages.hello", locale="en"), "Hello")
                    self.assertEqual(
                        i18n.t("nested.messages.hello", locale="fr"), "Bonjour"
                    )
                self.assertNotIn("de", translations.container)
                self.assertEqual(config.get("locale"), "en")

    def test_package_preload_respects_selected_locale_and_locale_only_filenames(self):
        config.set("load_path", [])
        config.set("filename_format", "{locale}.{format}")
        config.set(
            "load_package_path",
            [
                self.package(
                    "preload_locales",
                    {
                        "en.json": {"en": {"hello": "Hello"}},
                        "nested/fr.json": {"fr": {"hello": "Bonjour"}},
                    },
                )
            ],
        )
        i18n.load_all(["fr"])
        self.assertEqual(translations.get("nested.hello", "fr"), "Bonjour")
        self.assertNotIn("en", translations.container)

    def test_package_preload_preserves_source_precedence(self):
        self.write("messages.en.json", {"en": {"hello": "File", "file": "Kept"}})
        config.set(
            "load_package_path",
            [
                self.package(
                    "preload_first",
                    {
                        "messages.en.json": {
                            "en": {"hello": "First", "package": "Kept"}
                        },
                    },
                ),
                self.package(
                    "preload_last", {"messages.en.json": {"en": {"hello": "Last"}}}
                ),
            ],
        )
        i18n.load_all(["en"])
        self.assertEqual(translations.get("messages.hello", "en"), "Last")
        self.assertEqual(translations.get("messages.file", "en"), "Kept")
        self.assertEqual(translations.get("messages.package", "en"), "Kept")

    def test_package_preload_uses_format_namespace_root_and_encoding_settings(self):
        config.set("load_path", [])
        config.set("filename_format", "translations-{namespace}-{locale}.{format}")
        config.set("namespace_delimiter", "/")
        config.set("skip_locale_root_data", True)
        config.set("encoding", "cp1252")
        config.set(
            "load_package_path",
            [
                self.package(
                    "preload_configured",
                    {
                        "nested/translations-messages-fr.json": {"hello": "Salut é"},
                    },
                )
            ],
        )
        i18n.load_all(["fr"])
        self.assertEqual(translations.get("nested/messages/hello", "fr"), "Salut é")

    def test_malformed_package_file_is_reported_at_startup(self):
        config.set("load_path", [])
        config.set(
            "load_package_path",
            [
                self.package(
                    "preload_malformed",
                    {
                        "messages.en.json": "{",
                    },
                )
            ],
        )
        with self.assertRaises(i18n.I18nFileLoadError):
            i18n.load_all()

    def test_missing_package_is_reported_at_startup(self):
        config.set("load_path", [])
        config.set("load_package_path", ["i18n_missing_preload_package"])
        with self.assertRaises(ModuleNotFoundError):
            i18n.load_all()

    def test_python_package_resources_are_rejected_at_startup(self):
        config.set("load_path", [])
        config.set("file_format", "py")
        config.set("load_package_path", [self.package("preload_python", {})])
        with self.assertRaisesRegex(i18n.I18nFileLoadError, "text-based"):
            i18n.load_all()
