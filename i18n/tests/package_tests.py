import copy
import json
import os
import sys
import tempfile
import unittest
import zipfile

from i18n import config, resource_loader, translations
from i18n.translator import t


class TestPackageResources(unittest.TestCase):
    def setUp(self):
        self.settings = copy.deepcopy(config.settings)
        self.translations = translations.container
        self.loaders = resource_loader.loaders.copy()
        translations.container = {}
        config.set("load_path", [])
        config.set("load_package_path", ["i18n_test_resources"])
        config.set("file_format", "json")
        config.set("namespace_delimiter", ".")
        config.set("skip_locale_root_data", False)
        config.set("enable_memoization", False)
        config.set("encoding", "utf-8")
        config.set("filename_format", "{namespace}.{locale}.{format}")
        resource_loader.init_loaders()
        self.directory = tempfile.TemporaryDirectory()
        self.archive = os.path.join(self.directory.name, "resources.zip")
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("i18n_test_resources/__init__.py", "")
            archive.writestr(
                "i18n_test_resources/greetings.en.json",
                json.dumps({"en": {"hello": "Hello", "bye": "Goodbye"}}),
            )
            archive.writestr(
                "i18n_test_resources/greetings.fr.json",
                json.dumps({"fr": {"hello": "Bonjour"}}),
            )
            archive.writestr(
                "i18n_test_resources/en.json",
                json.dumps({"en": {"hello": "Hello from root"}}),
            )
            archive.writestr(
                "i18n_test_resources/nested/greetings.en.json",
                json.dumps({"en": {"hello": "Nested"}}),
            )
            archive.writestr(
                "i18n_test_resources/raw.en.json", json.dumps({"hello": "Raw"})
            )
            archive.writestr(
                "i18n_test_resources/greetings.en.yml", 'en:\n  hello: "你好"\n'
            )
        sys.path.insert(0, self.archive)

    def tearDown(self):
        sys.path.remove(self.archive)
        sys.modules.pop("i18n_test_resources", None)
        sys.path_importer_cache.pop(self.archive, None)
        config.settings.clear()
        config.settings.update(self.settings)
        translations.container = self.translations
        resource_loader.loaders = self.loaders
        self.directory.cleanup()

    def test_zip_package_json_and_locale(self):
        self.assertEqual(t("greetings.hello", locale="en"), "Hello")
        self.assertEqual(t("greetings.hello", locale="fr"), "Bonjour")

    def test_zip_package_nested_namespace(self):
        self.assertEqual(t("nested.greetings.hello", locale="en"), "Nested")
        config.set("namespace_delimiter", "/")
        translations.container = {}
        self.assertEqual(t("nested/greetings/hello", locale="en"), "Nested")

    def test_zip_package_without_filename_namespace(self):
        config.set("filename_format", "{locale}.{format}")
        self.assertEqual(t("hello", locale="en"), "Hello from root")

    def test_zip_locale_only_files_in_directory_namespaces(self):
        with zipfile.ZipFile(self.archive, "a") as archive:
            archive.writestr(
                "i18n_test_resources/nested/en.json",
                json.dumps({"en": {"hello": "Nested locale file"}}),
            )
            archive.writestr(
                "i18n_test_resources/nested/deep/en.json",
                json.dumps({"en": {"hello": "Deep locale file"}}),
            )
        config.set("filename_format", "{locale}.{format}")
        self.assertEqual(t("nested.hello", locale="en"), "Nested locale file")
        self.assertEqual(t("nested.deep.hello", locale="en"), "Deep locale file")
        self.assertEqual(t("hello", locale="en"), "Hello from root")

    def test_zip_package_without_locale_root(self):
        config.set("skip_locale_root_data", True)
        self.assertEqual(t("raw.hello", locale="en"), "Raw")

    def test_zip_package_yaml_encoding(self):
        config.set("file_format", "yml")
        self.assertEqual(t("greetings.hello", locale="en"), "你好")

    def test_zip_package_missing_file(self):
        self.assertEqual(t("missing.hello", locale="en"), "missing.hello")

    def test_filesystem_package(self):
        package = os.path.join(self.directory.name, "plain_test_resources")
        os.mkdir(package)
        for filename, content in (
            ("__init__.py", ""),
            ("greetings.en.json", json.dumps({"en": {"hello": "Plain package"}})),
        ):
            with open(os.path.join(package, filename), "w", encoding="utf-8") as handle:
                handle.write(content)
        sys.path.insert(0, self.directory.name)
        try:
            config.set("load_package_path", ["plain_test_resources"])
            self.assertEqual(t("greetings.hello", locale="en"), "Plain package")
        finally:
            sys.path.remove(self.directory.name)
            sys.modules.pop("plain_test_resources", None)
            sys.path_importer_cache.pop(self.directory.name, None)

    def test_python_package_loader_is_rejected(self):
        config.set("file_format", "py")
        with self.assertRaisesRegex(resource_loader.I18nFileLoadError, "text-based"):
            t("greetings.hello", locale="en")

    def test_zip_package_memoization(self):
        config.set("enable_memoization", True)
        self.assertEqual(t("greetings.hello", locale="en"), "Hello")
        translations.container = {}
        self.assertEqual(t("greetings.bye", locale="en"), "Goodbye")
        self.assertEqual(len(resource_loader.loaders["json"].memoization_dict), 1)
