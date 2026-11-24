import json
import os
import os.path
import tempfile
import unittest

# Python 3 only: always import reload from importlib
from importlib import reload
from pathlib import Path

from i18n import config, resource_loader, translations
from i18n.config import json_available, yaml_available
from i18n.resource_loader import I18nFileLoadError
from i18n.translator import t

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
        with self.assertRaisesRegex(I18nFileLoadError, "no loader .*"):
            resource_loader.load_resource("foo.bar", "baz")
            with self.assertRaisesRegex(I18nFileLoadError, "no loader .*"):
                resource_loader.load_resource("foo.bar", "baz")

    def test_register_wrong_loader(self):
        class WrongLoader:
            pass

        with self.assertRaises(ValueError):
            resource_loader.register_loader(WrongLoader, [])

    def test_register_python_loader(self):
        resource_loader.init_python_loader()
        with self.assertRaisesRegex(I18nFileLoadError, "error loading file .*"):
            resource_loader.load_resource("foo.py", "bar")
            with self.assertRaisesRegex(I18nFileLoadError, "error loading file .*"):
                resource_loader.load_resource("foo.py", "bar")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_register_yaml_loader(self):
        resource_loader.init_yaml_loader()
        with self.assertRaisesRegex(I18nFileLoadError, "error loading file .*"):
            resource_loader.load_resource("foo.yml", "bar")
            with self.assertRaisesRegex(I18nFileLoadError, "error loading file .*"):
                resource_loader.load_resource("foo.yml", "bar")

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_wrong_json_file(self):
        resource_loader.init_json_loader()
        with self.assertRaisesRegex(I18nFileLoadError, "error getting data .*"):
            resource_loader.load_resource(
                os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "foo"
            )
            with self.assertRaisesRegex(I18nFileLoadError, "error getting data .*"):
                resource_loader.load_resource(
                    os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"),
                    "foo",
                )

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_yaml_file(self):
        resource_loader.init_yaml_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.yml"), "settings"
        )
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_json_file(self):
        resource_loader.init_json_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.json"), "settings"
        )
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    def test_load_python_file(self):
        resource_loader.init_python_loader()
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "dummy_config.py"), "settings"
        )
        self.assertIn("foo", data)
        self.assertEqual("bar", data["foo"])

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_memoization_with_file(self):
        """This test creates a temporary file with the help of the
        tempfile library and writes a simple key: value dictionary in it.
        It will then use that file to load the translations and, after having
        enabled memoization, try to access it, causing the file to be (hopefully)
        memoized. It will then _remove_ the temporary file and try to access again,
        asserting that an error is not raised, thus making sure the data is
        actually loaded from memory and not from disk access."""
        memoization_file_name = "memoize.en.yml"
        # create the file and write the data in it
        try:
            d = tempfile.TemporaryDirectory()
            tmp_dir_name = d.name
        except AttributeError:
            # we are running python2, use mkdtemp
            tmp_dir_name = tempfile.mkdtemp()
        with open(f"{tmp_dir_name}/{memoization_file_name}", "w") as fd:
            fd.write("en:\n  key: value")
        # create the loader and pass the file to it
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(memoization_file_name, tmp_dir_name)
        # try loading the value to make sure it's working
        self.assertEqual(t("memoize.key"), "value")
        # now delete the file and directory
        # we are running python2, delete manually
        import shutil

        shutil.rmtree(tmp_dir_name)
        # test the translation again to make sure it's loaded from memory
        self.assertEqual(t("memoize.key"), "value")

    def test_memoization_distinguishes_relative_paths_after_chdir(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("enable_memoization", True)
        config.set("load_path", ["."])
        original_directory = os.getcwd()
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
        ):
            for directory, key, text in (
                (first, "first", "First directory"),
                (second, "second", "Second directory"),
            ):
                with open(
                    os.path.join(directory, "greetings.en.json"), "w"
                ) as stream:
                    json.dump({"en": {key: text}}, stream)
            try:
                os.chdir(first)
                self.assertEqual(t("greetings.first"), "First directory")
                os.chdir(second)
                self.assertEqual(t("greetings.second"), "Second directory")
            finally:
                os.chdir(original_directory)

    def test_memoization_shares_relative_and_absolute_file_paths(self):
        resource_loader.init_json_loader()
        config.set("enable_memoization", True)
        original_directory = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text('{"settings": {"greeting": "Hello"}}', encoding="utf-8")
            try:
                os.chdir(directory)
                expected = resource_loader.load_resource("settings.json", "settings")
                path.unlink()
                self.assertEqual(
                    resource_loader.load_resource(path, "settings"), expected
                )
            finally:
                os.chdir(original_directory)

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_file_with_strange_encoding(self):
        resource_loader.init_json_loader()
        config.set("encoding", "euc-jp")
        data = resource_loader.load_resource(
            os.path.join(RESOURCE_FOLDER, "settings", "eucjp_config.json"), "settings"
        )
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

    def test_namespace_after_other_filename_fields(self):
        for filename_format, filename in (
            ("{locale}.{namespace}.{format}", "ja.foo.yml"),
            ("translations.{namespace}.{locale}.{format}", "translations.foo.en.yml"),
        ):
            with self.subTest(filename_format=filename_format):
                config.set("filename_format", filename_format)
                self.assertEqual(
                    resource_loader.get_namespace_from_filepath(filename), "foo"
                )
                self.assertEqual(
                    resource_loader.get_namespace_from_filepath(
                        os.path.join("app", filename)
                    ),
                    "app.foo",
                )

    def test_missing_namespace_field_raises_loader_error(self):
        config.set("filename_format", "{locale}.{namespace}.{format}")
        with self.assertRaises(I18nFileLoadError):
            resource_loader.get_namespace_from_filepath("en")

    def test_translation_with_locale_first_filename(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("filename_format", "{locale}.{namespace}.{format}")
        with tempfile.TemporaryDirectory() as directory:
            with open(
                os.path.join(directory, "en.custom_filename.json"),
                "w",
                encoding="utf-8",
            ) as resource:
                resource.write('{"en": {"greeting": "Hello"}}')
            config.set("load_path", [directory])
            self.assertEqual(t("custom_filename.greeting"), "Hello")

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_translation_file(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(
            "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
        )

        self.assertTrue(translations.has("foo.normal_key"))
        self.assertTrue(translations.has("foo.parent.nested_key"))

    @unittest.skipUnless(json_available, "json library not available")
    def test_load_plural(self):
        resource_loader.init_yaml_loader()
        resource_loader.load_translation_file(
            "foo.en.yml", os.path.join(RESOURCE_FOLDER, "translations")
        )
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

    def test_search_skips_directory_named_translation_file(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
        ):
            os.mkdir(os.path.join(first, "greetings.en.json"))
            with open(os.path.join(second, "greetings.en.json"), "w") as stream:
                json.dump({"en": {"hello": "Hello"}}, stream)
            config.set("load_path", [first, second])
            self.assertEqual(t("greetings.hello"), "Hello")

    def test_search_skips_file_named_namespace_directory(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
        ):
            with open(os.path.join(first, "nested"), "w") as stream:
                stream.write("An unrelated file")
            os.mkdir(os.path.join(second, "nested"))
            with open(
                os.path.join(second, "nested", "greetings.en.json"), "w"
            ) as stream:
                json.dump({"en": {"hello": "Hello"}}, stream)
            config.set("load_path", [first, second])
            self.assertEqual(t("nested.greetings.hello"), "Hello")

    def test_search_descends_after_directory_named_translation_file(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        with tempfile.TemporaryDirectory() as directory:
            os.mkdir(os.path.join(directory, "nested.en.json"))
            os.mkdir(os.path.join(directory, "nested"))
            with open(
                os.path.join(directory, "nested", "greetings.en.json"), "w"
            ) as stream:
                json.dump({"en": {"hello": "Hello"}}, stream)
            config.set("load_path", [directory])
            self.assertEqual(t("nested.greetings.hello"), "Hello")

    def test_search_keeps_translation_file_errors(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "greetings.en.json"), "w") as stream:
                stream.write("[")
            config.set("load_path", [directory])
            with self.assertRaises(I18nFileLoadError):
                t("greetings.hello")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set("filename_format", "{locale}.{format}")
        resource_loader.search_translation("foo")
        self.assertTrue(translations.has("foo"))

    @unittest.skipUnless(yaml_available, "yaml library not available")
    def test_load_directory_does_not_match_locale_in_extension(self):
        resource_loader.init_yaml_loader()
        config.set("file_format", "yaml")
        config.set("filename_format", "{locale}.{format}")
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "de.yaml"), "w") as stream:
                stream.write("de:\n  greeting: Hallo\n")
            for locale in ("am", "ml"):
                with self.subTest(locale=locale):
                    resource_loader.load_directory(directory, locale)
                    self.assertFalse(translations.has("greeting", locale))

    def test_load_directory_matches_complete_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        for filename_format in ("{locale}.{format}", "english-{locale}.{format}"):
            with self.subTest(filename_format=filename_format):
                config.set("filename_format", filename_format)
                with tempfile.TemporaryDirectory() as directory:
                    for locale in ("zh-tw", "zh", "en", "de"):
                        filename = filename_format.format(locale=locale, format="json")
                        with open(os.path.join(directory, filename), "w") as stream:
                            json.dump({locale: {"greeting": locale}}, stream)
                    for locale in ("zh", "en"):
                        resource_loader.load_directory(directory, locale)
                        self.assertEqual(translations.get("greeting", locale), locale)

    def test_load_directory_keeps_filename_namespaces(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        with tempfile.TemporaryDirectory() as directory:
            for namespace, locale in (("foo", "en"), ("bar", "en"), ("english", "de")):
                filename = f"{namespace}.{locale}.json"
                with open(os.path.join(directory, filename), "w") as stream:
                    json.dump({locale: {"greeting": namespace}}, stream)
            resource_loader.load_directory(directory, "en")
            self.assertEqual(translations.get("foo.greeting", "en"), "foo")
            self.assertEqual(translations.get("bar.greeting", "en"), "bar")

    def test_search_without_namespace_respects_literal_filename(self):
        resource_loader.init_loaders()
        formats = ["json", "yml"] if yaml_available else ["json"]
        for file_format in formats:
            for filename_format in ("translations.{format}", "messages(1).{format}"):
                with self.subTest(format=file_format, filename=filename_format):
                    translations.container = {}
                    config.set("file_format", file_format)
                    config.set("filename_format", filename_format)
                    with tempfile.TemporaryDirectory() as directory:
                        filename = filename_format.format(format=file_format)
                        with open(os.path.join(directory, filename), "w") as stream:
                            json.dump({"en": {"greeting": "Hello"}}, stream)
                        # This file belongs to another tool and cannot be
                        # parsed as translations. Merely sharing the extension
                        # must not make it part of the configured resource.
                        with open(
                            os.path.join(directory, "synonyms." + file_format), "w"
                        ) as stream:
                            stream.write("[")
                        config.set("load_path", [directory])
                        self.assertEqual(t("greeting"), "Hello")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__default_locale(
        self,
    ):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("available_locales", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION")
        self.assertTrue(translations.has("COMMON.VERSION"))
        self.assertEqual(translations.get("COMMON.VERSION"), "version")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__two_levels_neting__other_locale(
        self,
    ):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("available_locales", ["en", "pl"])
        resource_loader.search_translation("COMMON.VERSION", locale="pl")
        self.assertTrue(translations.has("COMMON.VERSION", locale="pl"))
        self.assertEqual(translations.get("COMMON.VERSION", locale="pl"), "wersja")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__default_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS")
        self.assertTrue(translations.has("TOP_MENU.TOP_BAR.LOGS"))
        self.assertEqual(translations.get("TOP_MENU.TOP_BAR.LOGS"), "Logs")

    @unittest.skipUnless(json_available, "json library not available")
    def test_search_translation_without_ns_nested_dict__other_locale(self):
        resource_loader.init_json_loader()
        config.set("file_format", "json")
        config.set(
            "load_path",
            [os.path.join(RESOURCE_FOLDER, "translations", "nested_dict_json")],
        )
        config.set("filename_format", "{locale}.{format}")
        config.set("skip_locale_root_data", True)
        config.set("locale", "en")
        resource_loader.search_translation("TOP_MENU.TOP_BAR.LOGS", locale="pl")
        self.assertTrue(translations.has("TOP_MENU.TOP_BAR.LOGS", locale="pl"))
        self.assertEqual(translations.get("TOP_MENU.TOP_BAR.LOGS", locale="pl"), "Logi")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFileLoader)
unittest.TextTestRunner(verbosity=2).run(suite)
